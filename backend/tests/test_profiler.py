"""Unit tests for DataQualityProfiler and health score calculation."""

import numpy as np
import pandas as pd
import pytest
from app.services.profiler import DataQualityProfiler


@pytest.fixture
def profiler() -> DataQualityProfiler:
    return DataQualityProfiler()


def test_clean_dataset_profiling(profiler: DataQualityProfiler):
    """Verify metrics and high health score for clean tabular data."""
    df = pd.DataFrame(
        {
            "employee_id": [f"EMP_{i:03d}" for i in range(1, 51)],
            "department": ["Engineering", "Sales", "Marketing", "Finance", "HR"] * 10,
            "salary": np.linspace(60000, 150000, 50),
            "performance_rating": np.random.choice([3, 4, 5], size=50),
        }
    )

    profile = profiler.profile_dataframe(df)

    assert profile.total_rows == 50
    assert profile.total_columns == 4
    assert profile.total_missing_cells == 0
    assert profile.duplicate_rows == 0
    assert profile.health_score >= 90.0

    # Column level
    salary_col = profile.columns["salary"]
    assert salary_col.semantic_type in {"Numeric Continuous", "Numeric Discrete"}
    assert salary_col.numeric_stats is not None
    assert salary_col.numeric_stats.min == 60000.0
    assert salary_col.numeric_stats.max == 150000.0


def test_missing_values_and_empty_column(profiler: DataQualityProfiler):
    """Verify missing cell tracking and empty column penalty."""
    df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5],
            "metric_a": [10.0, None, 30.0, None, 50.0],
            "all_null": [None, None, None, None, None],
        }
    )

    profile = profiler.profile_dataframe(df)

    assert profile.total_missing_cells == 7  # 2 + 5
    assert profile.empty_columns == ["all_null"]
    assert profile.columns["metric_a"].missing_count == 2
    assert profile.columns["all_null"].semantic_type == "Empty"
    # Completeness score should be noticeably reduced
    assert profile.health_breakdown.completeness_score < 70.0


def test_duplicate_and_constant_columns(profiler: DataQualityProfiler):
    """Verify detection of duplicate rows and constant columns."""
    df = pd.DataFrame(
        {
            "country": ["USA", "USA", "USA", "USA", "USA"],  # Constant
            "env": ["prod", "prod", "prod", "prod", "prod"],  # Constant
            "val": [10, 10, 10, 20, 20],  # 3 duplicates
        }
    )

    profile = profiler.profile_dataframe(df)

    assert set(profile.constant_columns) == {"country", "env"}
    assert profile.duplicate_rows >= 2
    assert profile.health_breakdown.uniqueness_score < 60.0


def test_outlier_detection_iqr(profiler: DataQualityProfiler):
    """Verify Tukey IQR outlier identification on numeric series."""
    # Normal cluster around 10-20 with a massive outlier 1000
    df = pd.DataFrame(
        {"values": [10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 1000.0]}
    )

    profile = profiler.profile_dataframe(df)
    stats = profile.columns["values"].numeric_stats

    assert stats is not None
    assert stats.outliers_count == 1
    assert stats.outliers_percentage == 10.0


def test_suspicious_placeholders(profiler: DataQualityProfiler):
    """Verify detection of suspicious placeholders in text columns."""
    df = pd.DataFrame(
        {
            "code": [
                "valid",
                "?",
                "N/A",
                "none",
                "ok",
                "valid",
                "missing",
                "valid",
                "valid",
                "valid",
            ]
        }
    )

    profile = profiler.profile_dataframe(df)
    col = profile.columns["code"]

    assert col.suspicious_placeholder_count == 4  # ?, N/A, none, missing
    assert profile.health_breakdown.consistency_score < 100.0


def test_health_score_determinism(profiler: DataQualityProfiler):
    """Verify that health score is strictly deterministic and identical across repeated evaluations."""
    df = pd.DataFrame(
        {
            "x": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "y": ["A", "B", "A", "B", "A", "B", "A", "B", "A", "B"],
            "z": [10.5, 20.1, None, 40.2, 50.0, 60.1, 70.3, 80.4, 90.5, 100.0],
        }
    )

    score_1 = profiler.profile_dataframe(df).health_score
    score_2 = profiler.profile_dataframe(df).health_score

    assert score_1 == score_2
    assert 0.0 <= score_1 <= 100.0


def test_boundary_empty_dataframe(profiler: DataQualityProfiler):
    """Verify edge case of completely empty dataframe returns 0.0 score."""
    empty_df = pd.DataFrame()
    profile = profiler.profile_dataframe(empty_df)

    assert profile.total_rows == 0
    assert profile.total_columns == 0
    assert profile.health_score == 0.0
    assert profile.health_breakdown.composite_health_score == 0.0


def test_profile_to_dict_json_serializable(profiler: DataQualityProfiler):
    """Verify profile.to_dict() converts all NumPy and NaN floats safely."""
    df = pd.DataFrame(
        {
            "a": [1.0, float("nan"), 3.0],
            "b": ["x", "y", "z"],
        }
    )

    profile = profiler.profile_dataframe(df)
    profile_dict = profile.to_dict()

    import json

    # Must dump cleanly without TypeError
    dumped = json.dumps(profile_dict)
    assert "health_score" in dumped
    assert "columns" in dumped


def test_numeric_stats_with_infinite_values(profiler: DataQualityProfiler):
    """Verify that infinite values (inf, -inf) are handled safely without corrupting metrics."""
    df = pd.DataFrame(
        {
            "metric": [10.0, float("inf"), float("-inf"), 20.0, 30.0],
        }
    )

    profile = profiler.profile_dataframe(df)
    stats = profile.columns["metric"].numeric_stats
    assert stats is not None
    assert stats.count == 3
    assert stats.mean == 20.0
    assert stats.min == 10.0
    assert stats.max == 30.0
