"""Unit and integration tests for SQLAlchemy 2.0 ORM models."""

import uuid

import pytest
from app.models import (
    AgentStep,
    AnalysisReport,
    AnalysisSession,
    Base,
    Dataset,
    Workspace,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


def test_models_metadata_registration():
    """Verify all 5 required tables are registered with Base metadata."""
    expected_tables = {
        "workspaces",
        "datasets",
        "analysis_sessions",
        "agent_steps",
        "analysis_reports",
    }
    registered_tables = set(Base.metadata.tables.keys())
    assert expected_tables.issubset(registered_tables)


@pytest.mark.asyncio
async def test_create_workspace_and_dataset(db_session: AsyncSession):
    """Verify creating a Workspace and associated Dataset with relationship links."""
    # 1. Create Workspace
    workspace = Workspace(name="Finance Intelligence Hub", owner_id="user_test_123")
    db_session.add(workspace)
    await db_session.flush()

    assert isinstance(workspace.id, uuid.UUID)
    assert workspace.name == "Finance Intelligence Hub"

    # 2. Create Dataset referencing Workspace
    dataset = Dataset(
        workspace_id=workspace.id,
        file_name="q3_revenue.csv",
        file_path="/storage/datasets/q3_revenue.csv",
        file_size_bytes=1048576,
        mime_type="text/csv",
        row_count=15000,
        col_count=12,
        health_score=94.5,
    )
    db_session.add(dataset)
    await db_session.flush()

    assert isinstance(dataset.id, uuid.UUID)
    assert dataset.workspace_id == workspace.id
    assert dataset.health_score == 94.5


@pytest.mark.asyncio
async def test_full_analysis_workflow_hierarchy(db_session: AsyncSession):
    """Verify hierarchy from Workspace down to AnalysisSession, AgentStep, and AnalysisReport."""
    workspace = Workspace(name="Operations Workspace")
    db_session.add(workspace)
    await db_session.flush()

    dataset = Dataset(
        workspace_id=workspace.id,
        file_name="ops_log.csv",
        file_path="/storage/datasets/ops_log.csv",
        row_count=5000,
        col_count=8,
    )
    db_session.add(dataset)
    await db_session.flush()

    session = AnalysisSession(
        dataset_id=dataset.id,
        user_query="Why did delivery latency spike in September?",
        status="RUNNING",
    )
    db_session.add(session)
    await db_session.flush()

    # Add Agent Steps
    step1 = AgentStep(
        session_id=session.id,
        step_number=1,
        agent_name="SupervisorAgent",
        tool_name="analysis_plan",
        tool_args={"target_metric": "latency", "dimension": "month"},
        output={"plan_steps": ["eda", "t_test"]},
        duration_ms=45,
    )
    step2 = AgentStep(
        session_id=session.id,
        step_number=2,
        agent_name="StatisticalAgent",
        tool_name="t_test",
        tool_args={"group_col": "month", "metric_col": "latency"},
        output={"t_statistic": 4.12, "p_value": 0.0001},
        duration_ms=88,
    )
    db_session.add_all([step1, step2])
    await db_session.flush()

    # Add Final Report
    report = AnalysisReport(
        session_id=session.id,
        summary="Statistically significant latency increase identified in September.",
        payload={
            "key_drivers": ["carrier_delay", "region_east"],
            "statistical_significance": True,
        },
    )
    db_session.add(report)
    await db_session.flush()

    # Query back and verify relationships
    stmt = select(AnalysisSession).where(AnalysisSession.id == session.id)
    result = await db_session.execute(stmt)
    loaded_session = result.scalar_one()

    assert loaded_session.user_query == "Why did delivery latency spike in September?"
    assert len(loaded_session.agent_steps) == 2
    assert loaded_session.agent_steps[0].agent_name == "SupervisorAgent"
    assert loaded_session.agent_steps[1].agent_name == "StatisticalAgent"
    assert len(loaded_session.analysis_reports) == 1
    assert (
        loaded_session.analysis_reports[0].payload["statistical_significance"] is True
    )
