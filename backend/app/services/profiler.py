"""Automated tabular data quality profiler for Inferaxis.

Computes comprehensive deterministic profiling metrics, semantic type inferences,
descriptive statistics, outlier detection, and a multi-factor Data Health Score (0–100).
Never passes raw data to logs or LLMs.
"""

from __future__ import annotations

import logging
import math
import re
from dataclasses import asdict, dataclass, field
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger("inferaxis.profiler")

# Suspicious placeholder tokens commonly masquerading as valid data
SUSPICIOUS_STRING_TOKENS = {
    "na",
    "n/a",
    "null",
    "none",
    "nil",
    "nan",
    "?",
    "-",
    "--",
    ".",
    "undefined",
    "missing",
    "unknown",
    "#n/a",
    "#value!",
}


@dataclass
class NumericColumnStats:
    """Detailed descriptive statistics for a numeric column."""

    count: int
    mean: float | None
    std: float | None
    min: float | None
    p25: float | None
    median: float | None
    p75: float | None
    max: float | None
    iqr: float | None
    outliers_count: int
    outliers_percentage: float


@dataclass
class CategoricalValueFreq:
    """Frequency entry for top categorical values."""

    value: str
    count: int
    percentage: float


@dataclass
class ColumnProfile:
    """Comprehensive data quality profile for a single column."""

    name: str
    dtype: str
    semantic_type: str
    total_count: int
    missing_count: int
    missing_percentage: float
    distinct_count: int
    distinct_percentage: float
    is_constant: bool
    is_near_constant: bool
    dominant_value: str | None = None
    dominant_percentage: float | None = None
    numeric_stats: NumericColumnStats | None = None
    top_categories: list[CategoricalValueFreq] = field(default_factory=list)
    suspicious_placeholder_count: int = 0
    type_inconsistencies: int = 0


@dataclass
class HealthScoreBreakdown:
    """Detailed score components contributing to the composite Data Health Score (0–100)."""

    completeness_score: float  # 0 to 100
    uniqueness_score: float  # 0 to 100
    consistency_score: float  # 0 to 100
    structural_score: float  # 0 to 100
    composite_health_score: float  # 0 to 100
    evaluation_notes: list[str] = field(default_factory=list)


@dataclass
class DatasetQualityProfile:
    """Complete dataset quality profile produced by DataQualityProfiler."""

    total_rows: int
    total_columns: int
    total_cells: int
    total_missing_cells: int
    missing_cell_percentage: float
    duplicate_rows: int
    duplicate_percentage: float
    memory_usage_mb: float
    health_score: float
    health_breakdown: HealthScoreBreakdown
    columns: dict[str, ColumnProfile]
    constant_columns: list[str]
    near_constant_columns: list[str]
    empty_columns: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Convert profile to a JSON-serializable dictionary with sanitized floats."""
        raw = asdict(self)
        return self._sanitize_dict(raw)

    @classmethod
    def _sanitize_dict(cls, d: Any) -> Any:
        if isinstance(d, dict):
            return {k: cls._sanitize_dict(v) for k, v in d.items()}
        elif isinstance(d, list):
            return [cls._sanitize_dict(item) for item in d]
        elif isinstance(d, float):
            if math.isnan(d) or math.isinf(d):
                return None
            return round(d, 4)
        elif isinstance(d, (np.integer, np.floating)):
            val = d.item()
            if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
                return None
            return val
        return d


class DataQualityProfiler:
    """Autonomous profiling engine for tabular datasets in Inferaxis.

    Adheres strictly to deterministic statistical rules.
    Health Score is formulated to evaluate structural readiness, hygiene, and consistency.
    It does not claim to verify ground-truth real-world factuality.
    """

    def __init__(
        self,
        top_k_categories: int = 5,
        near_constant_threshold: float = 0.95,
    ) -> None:
        self.top_k_categories = top_k_categories
        self.near_constant_threshold = near_constant_threshold

    def profile_dataframe(self, df: pd.DataFrame) -> DatasetQualityProfile:
        """Execute complete quality profiling on a pandas DataFrame.

        Args:
            df: Tabular dataset to profile.

        Returns:
            DatasetQualityProfile containing detailed column diagnostics and health metrics.
        """
        total_rows = len(df)
        total_columns = len(df.columns)
        total_cells = total_rows * total_columns

        # Empty dataset edge case
        if total_rows == 0 or total_columns == 0:
            return self._build_empty_profile(total_rows, total_columns)

        # Dataset-level missing values & duplicates
        total_missing_cells = int(df.isna().sum().sum())
        missing_cell_percentage = (
            round((total_missing_cells / total_cells) * 100.0, 2)
            if total_cells > 0
            else 0.0
        )
        duplicate_rows = int(df.duplicated().sum())
        duplicate_percentage = (
            round((duplicate_rows / total_rows) * 100.0, 2) if total_rows > 0 else 0.0
        )

        # Memory footprint in MB
        memory_usage_mb = round(
            float(df.memory_usage(deep=True).sum()) / (1024 * 1024), 3
        )

        # Column-by-column profiling
        column_profiles: dict[str, ColumnProfile] = {}
        constant_columns: list[str] = []
        near_constant_columns: list[str] = []
        empty_columns: list[str] = []

        for col_name in df.columns:
            profile = self._profile_column(df[col_name], str(col_name), total_rows)
            column_profiles[str(col_name)] = profile

            if profile.missing_count == total_rows:
                empty_columns.append(str(col_name))
            if profile.is_constant:
                constant_columns.append(str(col_name))
            elif profile.is_near_constant:
                near_constant_columns.append(str(col_name))

        # Multi-factor Data Health Score calculation
        health_breakdown = self._calculate_health_score(
            total_rows=total_rows,
            total_columns=total_columns,
            total_missing_cells=total_missing_cells,
            total_cells=total_cells,
            duplicate_rows=duplicate_rows,
            column_profiles=column_profiles,
            constant_columns=constant_columns,
            empty_columns=empty_columns,
        )

        return DatasetQualityProfile(
            total_rows=total_rows,
            total_columns=total_columns,
            total_cells=total_cells,
            total_missing_cells=total_missing_cells,
            missing_cell_percentage=missing_cell_percentage,
            duplicate_rows=duplicate_rows,
            duplicate_percentage=duplicate_percentage,
            memory_usage_mb=memory_usage_mb,
            health_score=health_breakdown.composite_health_score,
            health_breakdown=health_breakdown,
            columns=column_profiles,
            constant_columns=constant_columns,
            near_constant_columns=near_constant_columns,
            empty_columns=empty_columns,
        )

    # -------------------------------------------------------------------------
    # Column-Level Diagnostics
    # -------------------------------------------------------------------------

    def _profile_column(
        self, series: pd.Series, col_name: str, total_rows: int
    ) -> ColumnProfile:
        missing_count = int(series.isna().sum())
        missing_percentage = (
            round((missing_count / total_rows) * 100.0, 2) if total_rows > 0 else 0.0
        )

        non_null_series = series.dropna()
        distinct_count = int(non_null_series.nunique())
        distinct_percentage = (
            round((distinct_count / total_rows) * 100.0, 2) if total_rows > 0 else 0.0
        )

        is_constant = distinct_count == 1
        is_near_constant = False
        dominant_value: str | None = None
        dominant_percentage: float | None = None

        if len(non_null_series) > 0 and distinct_count > 0:
            top_val_count = non_null_series.value_counts().iloc[0]
            dom_pct = top_val_count / len(non_null_series)
            if dom_pct >= self.near_constant_threshold and not is_constant:
                is_near_constant = True
                dominant_value = str(non_null_series.value_counts().index[0])
                dominant_percentage = round(dom_pct * 100.0, 2)

        # Semantic Classification
        semantic_type = self._classify_semantic_type(
            series, non_null_series, distinct_count, total_rows
        )

        # Numeric statistics & outliers
        numeric_stats: NumericColumnStats | None = None
        if pd.api.types.is_numeric_dtype(series) and not pd.api.types.is_bool_dtype(
            series
        ):
            numeric_stats = self._compute_numeric_stats(non_null_series)

        # Categorical frequencies (top N)
        top_categories: list[CategoricalValueFreq] = []
        if (
            semantic_type
            in {
                "Categorical Nominal",
                "Categorical Ordinal",
                "Boolean",
                "Numeric Discrete",
            }
            and distinct_count > 0
        ):
            top_categories = self._compute_top_categories(non_null_series)

        # Suspicious string values and type inconsistencies
        suspicious_count, inconsistencies = self._inspect_inconsistencies(
            series, non_null_series, semantic_type
        )

        return ColumnProfile(
            name=col_name,
            dtype=str(series.dtype),
            semantic_type=semantic_type,
            total_count=total_rows,
            missing_count=missing_count,
            missing_percentage=missing_percentage,
            distinct_count=distinct_count,
            distinct_percentage=distinct_percentage,
            is_constant=is_constant,
            is_near_constant=is_near_constant,
            dominant_value=dominant_value,
            dominant_percentage=dominant_percentage,
            numeric_stats=numeric_stats,
            top_categories=top_categories,
            suspicious_placeholder_count=suspicious_count,
            type_inconsistencies=inconsistencies,
        )

    def _classify_semantic_type(
        self,
        full_series: pd.Series,
        non_null_series: pd.Series,
        distinct_count: int,
        total_rows: int,
    ) -> str:
        """Classify a column into formal Inferaxis semantic data types."""
        if len(non_null_series) == 0:
            return "Empty"

        # Boolean
        if pd.api.types.is_bool_dtype(full_series) or (
            distinct_count == 2
            and set(non_null_series.astype(str).str.lower().unique()).issubset(
                {"true", "false", "0", "1", "yes", "no"}
            )
        ):
            return "Boolean"

        # Unique Identifier
        col_lower = str(full_series.name).lower()
        if (
            distinct_count == total_rows
            and (
                col_lower in {"id", "uuid", "guid", "key"}
                or col_lower.endswith(("_id", "_uuid", "_key"))
                or distinct_count > 100
            )
            and not pd.api.types.is_float_dtype(full_series)
        ):
            return "Unique Identifier"

        # Datetime
        if pd.api.types.is_datetime64_any_dtype(full_series):
            return "Datetime / Timestamp"

        # Try parsing strings as datetime for small sample if object column
        if pd.api.types.is_object_dtype(full_series):
            sample = non_null_series.head(20).astype(str)
            # Check for common ISO date patterns (YYYY-MM-DD or YYYY/MM/DD)
            date_matches = sample.str.match(r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}").sum()
            if date_matches >= len(sample) * 0.8:
                try:
                    pd.to_datetime(sample, errors="raise")
                except (ValueError, TypeError, pd.errors.OutOfBoundsDatetime):
                    pass

        # Numeric types
        if pd.api.types.is_numeric_dtype(full_series):
            if pd.api.types.is_integer_dtype(full_series):
                return "Numeric Discrete"
            return "Numeric Continuous"

        # Text types
        if pd.api.types.is_object_dtype(full_series) or pd.api.types.is_string_dtype(
            full_series
        ):
            # Compute average string length
            str_lens = non_null_series.astype(str).str.len()
            avg_len = str_lens.mean() if len(str_lens) > 0 else 0.0

            if avg_len > 100 or str_lens.max() > 250:
                return "Freeform Text"

            # Check for low cardinality categoricals
            if distinct_count <= 30 or (
                total_rows > 0 and distinct_count / total_rows < 0.2
            ):
                return "Categorical Nominal"

            return "Freeform Text"

        return "Categorical Nominal"

    def _compute_numeric_stats(
        self, non_null_series: pd.Series
    ) -> NumericColumnStats | None:
        """Compute verified IQR bounds and numeric summaries."""
        if len(non_null_series) == 0:
            return None

        # Cast to float64 safely, filtering out non-numeric and infinite values
        s = (
            pd.to_numeric(non_null_series, errors="coerce")
            .replace([np.inf, -np.inf], np.nan)
            .dropna()
        )
        if len(s) == 0:
            return None

        count = len(s)
        mean_val = float(s.mean())
        std_val = float(s.std()) if count > 1 else 0.0
        min_val = float(s.min())
        p25 = float(s.quantile(0.25))
        median_val = float(s.median())
        p75 = float(s.quantile(0.75))
        max_val = float(s.max())

        # Interquartile Range & Outlier Bounds (Tukey's method)
        iqr = p75 - p25
        lower_bound = p25 - (1.5 * iqr)
        upper_bound = p75 + (1.5 * iqr)

        outliers = s[(s < lower_bound) | (s > upper_bound)]
        outliers_count = len(outliers)
        outliers_pct = round((outliers_count / count) * 100.0, 2) if count > 0 else 0.0

        return NumericColumnStats(
            count=count,
            mean=round(mean_val, 4),
            std=round(std_val, 4) if not math.isnan(std_val) else 0.0,
            min=round(min_val, 4),
            p25=round(p25, 4),
            median=round(median_val, 4),
            p75=round(p75, 4),
            max=round(max_val, 4),
            iqr=round(iqr, 4),
            outliers_count=outliers_count,
            outliers_percentage=outliers_pct,
        )

    def _compute_top_categories(
        self, non_null_series: pd.Series
    ) -> list[CategoricalValueFreq]:
        """Compute top N value frequencies for a categorical column."""
        total = len(non_null_series)
        if total == 0:
            return []

        counts = non_null_series.value_counts().head(self.top_k_categories)
        results: list[CategoricalValueFreq] = []
        for val, count in counts.items():
            str_val = str(val)[
                :50
            ]  # Truncate length to prevent leakage or bloated JSON
            pct = round((count / total) * 100.0, 2)
            results.append(
                CategoricalValueFreq(value=str_val, count=int(count), percentage=pct)
            )
        return results

    def _inspect_inconsistencies(
        self,
        full_series: pd.Series,
        non_null_series: pd.Series,
        semantic_type: str,
    ) -> tuple[int, int]:
        """Identify suspicious placeholders and type conversion discrepancies."""
        suspicious_count = 0
        inconsistencies = 0

        if pd.api.types.is_object_dtype(full_series) or pd.api.types.is_string_dtype(
            full_series
        ):
            str_series = non_null_series.astype(str).str.strip().str.lower()
            suspicious_count = int(str_series.isin(SUSPICIOUS_STRING_TOKENS).sum())

            # Check if an object column actually contains mostly numeric digits
            if semantic_type not in {"Numeric Continuous", "Numeric Discrete"}:
                numeric_matches = str_series.str.match(r"^-?\d+(\.\d+)?$").sum()
                if 0 < numeric_matches < len(str_series):
                    # Mixed numbers and non-numeric strings
                    inconsistencies = int(numeric_matches)

        return suspicious_count, inconsistencies

    # -------------------------------------------------------------------------
    # Data Health Score Formulation
    # -------------------------------------------------------------------------

    def _calculate_health_score(
        self,
        total_rows: int,
        total_columns: int,
        total_missing_cells: int,
        total_cells: int,
        duplicate_rows: int,
        column_profiles: dict[str, ColumnProfile],
        constant_columns: list[str],
        empty_columns: list[str],
    ) -> HealthScoreBreakdown:
        """Calculate documented, deterministic Data Health Score (0–100).

        Formula Architecture:
        1. Completeness Score (Weight: 35%)
           - Cell fill rate: 1.0 - (missing_cells / total_cells)
           - Empty column penalty: (empty_cols / total_cols) * 0.5
        2. Uniqueness Score (Weight: 25%)
           - Duplicate row ratio: 1.0 - (duplicate_rows / total_rows)
           - Constant column penalty: zero variance across rows contributes no analytical value.
        3. Consistency & Outlier Score (Weight: 25%)
           - Penalizes suspicious placeholder strings ("?", "N/A", "missing").
           - Penalizes extreme outliers in numeric fields.
        4. Structural Readiness Score (Weight: 15%)
           - Proportion of clean column names vs auto-generated 'unnamed_N'.
           - Penalizes micro-datasets with insufficient analytical power (<5 rows).

        Limitations:
        - Health Score measures technical completeness and schema integrity.
        - It does NOT evaluate whether numerical values correspond to real-world ground truth.
        """
        notes: list[str] = []

        # 1. Completeness (0 to 100)
        cell_fill_rate = (
            1.0 - (total_missing_cells / total_cells) if total_cells > 0 else 0.0
        )
        empty_col_penalty = (
            (len(empty_columns) / total_columns) if total_columns > 0 else 0.0
        )
        raw_completeness = max(0.0, cell_fill_rate - (empty_col_penalty * 0.4))
        completeness_score = round(raw_completeness * 100.0, 2)

        if total_missing_cells > 0:
            notes.append(
                f"Missing values present: {total_missing_cells} cells ({round((total_missing_cells / total_cells) * 100.0, 1)}% of dataset)."
            )
        if empty_columns:
            notes.append(f"Contains {len(empty_columns)} completely empty column(s).")

        # 2. Uniqueness (0 to 100)
        dup_ratio = (duplicate_rows / total_rows) if total_rows > 0 else 0.0
        const_col_ratio = (
            (len(constant_columns) / total_columns) if total_columns > 0 else 0.0
        )
        raw_uniqueness = max(0.0, (1.0 - dup_ratio) - (const_col_ratio * 0.3))
        uniqueness_score = round(raw_uniqueness * 100.0, 2)

        if duplicate_rows > 0:
            notes.append(
                f"Duplicate rows detected: {duplicate_rows} ({round(dup_ratio * 100.0, 1)}% of rows)."
            )
        if constant_columns:
            notes.append(
                f"Contains {len(constant_columns)} constant column(s) with zero analytical variance."
            )

        # 3. Consistency (0 to 100)
        total_suspicious = sum(
            p.suspicious_placeholder_count for p in column_profiles.values()
        )
        total_inconsistencies = sum(
            p.type_inconsistencies for p in column_profiles.values()
        )
        total_outliers = sum(
            p.numeric_stats.outliers_count
            for p in column_profiles.values()
            if p.numeric_stats is not None
        )

        suspicious_ratio = (total_suspicious / total_cells) if total_cells > 0 else 0.0
        inconsistency_ratio = (
            (total_inconsistencies / total_cells) if total_cells > 0 else 0.0
        )
        outlier_ratio = (total_outliers / total_cells) if total_cells > 0 else 0.0

        raw_consistency = max(
            0.0,
            1.0
            - (suspicious_ratio * 2.5)
            - (inconsistency_ratio * 2.0)
            - (min(outlier_ratio, 0.2) * 0.5),
        )
        consistency_score = round(raw_consistency * 100.0, 2)

        if total_suspicious > 0:
            notes.append(
                f"Detected {total_suspicious} suspicious string placeholder(s)."
            )
        if total_inconsistencies > 0:
            notes.append(
                f"Found {total_inconsistencies} type inconsistencies in textual columns."
            )

        # 4. Structural Readiness (0 to 100)
        unnamed_cols = sum(
            1 for name in column_profiles if re.match(r"^unnamed_\d+$", name)
        )
        unnamed_ratio = (unnamed_cols / total_columns) if total_columns > 0 else 0.0
        sample_penalty = 0.5 if total_rows < 5 else (0.2 if total_rows < 20 else 0.0)

        raw_structure = max(0.0, (1.0 - unnamed_ratio) - sample_penalty)
        structural_score = round(raw_structure * 100.0, 2)

        if unnamed_cols > 0:
            notes.append(f"{unnamed_cols} column(s) lacked valid header names.")
        if total_rows < 5:
            notes.append(
                "Dataset has fewer than 5 rows, limiting statistical significance."
            )

        # Composite Weighted Score
        composite = (
            (completeness_score * 0.35)
            + (uniqueness_score * 0.25)
            + (consistency_score * 0.25)
            + (structural_score * 0.15)
        )
        composite_health_score = round(max(0.0, min(100.0, composite)), 2)

        if not notes:
            notes.append(
                "Dataset meets all standard hygiene and completeness baselines."
            )

        return HealthScoreBreakdown(
            completeness_score=completeness_score,
            uniqueness_score=uniqueness_score,
            consistency_score=consistency_score,
            structural_score=structural_score,
            composite_health_score=composite_health_score,
            evaluation_notes=notes,
        )

    def _build_empty_profile(
        self, total_rows: int, total_columns: int
    ) -> DatasetQualityProfile:
        """Construct deterministic zero-bound profile for empty datasets."""
        breakdown = HealthScoreBreakdown(
            completeness_score=0.0,
            uniqueness_score=0.0,
            consistency_score=0.0,
            structural_score=0.0,
            composite_health_score=0.0,
            evaluation_notes=["Dataset is completely empty (0 rows or 0 columns)."],
        )
        return DatasetQualityProfile(
            total_rows=total_rows,
            total_columns=total_columns,
            total_cells=0,
            total_missing_cells=0,
            missing_cell_percentage=0.0,
            duplicate_rows=0,
            duplicate_percentage=0.0,
            memory_usage_mb=0.0,
            health_score=0.0,
            health_breakdown=breakdown,
            columns={},
            constant_columns=[],
            near_constant_columns=[],
            empty_columns=[],
        )
