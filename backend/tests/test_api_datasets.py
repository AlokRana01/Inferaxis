"""Integration tests for Dataset API endpoints."""

import io
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

import openpyxl
import pytest
from app.models.workspace import Workspace
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_upload_csv_endpoint_success(
    async_client: AsyncClient, db_session: AsyncSession
):
    """Verify POST /api/v1/datasets/upload with valid CSV."""
    # Ensure a workspace exists
    workspace = Workspace(name="Test Hub", owner_id="user_api")
    db_session.add(workspace)
    await db_session.flush()

    csv_content = b"col_a,col_b,metric\nalpha,10,99.5\nbeta,20,88.2\n"
    files = {"file": ("test_data.csv", io.BytesIO(csv_content), "text/csv")}
    data = {"workspace_id": str(workspace.id)}

    response = await async_client.post(
        "/api/v1/datasets/upload", files=files, data=data
    )
    assert response.status_code == 201
    payload = response.json()

    assert "id" in payload
    assert payload["file_name"] == "test_data.csv"
    assert payload["row_count"] == 2
    assert payload["col_count"] == 3
    assert payload["health_score"] > 80.0
    assert payload["schema_metadata"]["delimiter"] == ","
    assert "columns" in payload["schema_metadata"]


@pytest.mark.asyncio
async def test_upload_xlsx_endpoint_success(
    async_client: AsyncClient, db_session: AsyncSession
):
    """Verify POST /api/v1/datasets/upload with valid XLSX workbook."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sales"
    ws.append(["quarter", "amount"])
    ws.append(["Q1", 1000])
    ws.append(["Q2", 2000])

    buf = io.BytesIO()
    wb.save(buf)
    wb.close()
    buf.seek(0)

    files = {
        "file": (
            "financials.xlsx",
            buf,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }

    response = await async_client.post("/api/v1/datasets/upload", files=files)
    assert response.status_code == 201
    payload = response.json()

    assert payload["file_name"] == "financials.xlsx"
    assert payload["row_count"] == 2
    assert payload["col_count"] == 2


@pytest.mark.asyncio
async def test_upload_empty_file_rejected(async_client: AsyncClient):
    """Verify POST /api/v1/datasets/upload rejects 0-byte file with 400 Bad Request."""
    files = {"file": ("empty.csv", io.BytesIO(b""), "text/csv")}
    response = await async_client.post("/api/v1/datasets/upload", files=files)

    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_upload_unsupported_format_rejected(async_client: AsyncClient):
    """Verify POST /api/v1/datasets/upload rejects unsupported extension with 415."""
    files = {"file": ("notes.pdf", io.BytesIO(b"pdf data"), "application/pdf")}
    response = await async_client.post("/api/v1/datasets/upload", files=files)

    assert response.status_code == 415
    assert "unsupported" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_dataset_and_profile_endpoints(async_client: AsyncClient):
    """Verify GET /api/v1/datasets/{id} and GET /api/v1/datasets/{id}/profile."""
    csv_content = b"user_id,score\n1,95\n2,88\n"
    files = {"file": ("scores.csv", io.BytesIO(csv_content), "text/csv")}

    create_res = await async_client.post("/api/v1/datasets/upload", files=files)
    assert create_res.status_code == 201
    dataset_id = create_res.json()["id"]

    # 1. GET metadata
    get_res = await async_client.get(f"/api/v1/datasets/{dataset_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == dataset_id
    assert get_res.json()["file_name"] == "scores.csv"

    # 2. GET profile
    profile_res = await async_client.get(f"/api/v1/datasets/{dataset_id}/profile")
    assert profile_res.status_code == 200
    p_data = profile_res.json()
    assert p_data["dataset_id"] == dataset_id
    assert "health_score" in p_data
    assert "profile_summary" in p_data
    assert p_data["profile_summary"]["total_rows"] == 2

    # 3. Nonexistent ID -> 404
    fake_id = str(uuid.uuid4())
    notFound_res = await async_client.get(f"/api/v1/datasets/{fake_id}")
    assert notFound_res.status_code == 404


@pytest.mark.asyncio
async def test_workspace_isolation_cross_access_prevented(
    async_client: AsyncClient, db_session: AsyncSession
):
    """Verify that a dataset created in Workspace A cannot be accessed with Workspace B's ID."""
    ws_a = Workspace(name="Workspace Alpha", owner_id="user_alpha")
    ws_b = Workspace(name="Workspace Beta", owner_id="user_beta")
    db_session.add_all([ws_a, ws_b])
    await db_session.flush()

    csv_content = b"k,v\n1,100\n2,200\n"
    files = {"file": ("alpha_data.csv", io.BytesIO(csv_content), "text/csv")}
    upload_res = await async_client.post(
        "/api/v1/datasets/upload",
        files=files,
        data={"workspace_id": str(ws_a.id)},
    )
    assert upload_res.status_code == 201
    dataset_id = upload_res.json()["id"]

    # 1. Querying with the correct Workspace A ID succeeds
    correct_ws_res = await async_client.get(
        f"/api/v1/datasets/{dataset_id}",
        params={"workspace_id": str(ws_a.id)},
    )
    assert correct_ws_res.status_code == 200
    assert correct_ws_res.json()["id"] == dataset_id

    # 2. Querying with Workspace B ID is rejected with 404
    cross_ws_res = await async_client.get(
        f"/api/v1/datasets/{dataset_id}",
        params={"workspace_id": str(ws_b.id)},
    )
    assert cross_ws_res.status_code == 404
    assert "not found in workspace" in cross_ws_res.json()["detail"].lower()

    # 3. Profile retrieval with Workspace B ID is also rejected with 404
    cross_profile_res = await async_client.get(
        f"/api/v1/datasets/{dataset_id}/profile",
        params={"workspace_id": str(ws_b.id)},
    )
    assert cross_profile_res.status_code == 404


@pytest.mark.asyncio
async def test_generate_ai_insights_endpoint(
    async_client: AsyncClient, db_session: AsyncSession
):
    """Verify POST /api/v1/datasets/{dataset_id}/ai-insights returns structured AI summary."""
    workspace = Workspace(name="Insights Hub", owner_id="user_insights")
    db_session.add(workspace)
    await db_session.flush()

    csv_content = b"feature_1,feature_2,label\n1.2,3.4,0\n5.6,7.8,1\n"
    files = {"file": ("insights_data.csv", io.BytesIO(csv_content), "text/csv")}
    upload_res = await async_client.post(
        "/api/v1/datasets/upload",
        files=files,
        data={"workspace_id": str(workspace.id)},
    )
    dataset_id = upload_res.json()["id"]

    with patch("app.services.dataset_service.get_llm_router") as mock_router_getter:
        mock_router = MagicMock()
        mock_router.settings.LLM_PROVIDER = "groq"
        mock_router.complete = AsyncMock(
            return_value="### Executive Summary\nHigh-quality dataset ready for classification."
        )
        mock_router_getter.return_value = mock_router

        response = await async_client.post(
            f"/api/v1/datasets/{dataset_id}/ai-insights",
            params={"workspace_id": str(workspace.id)},
        )

        assert response.status_code == 200
        payload = response.json()
        assert payload["dataset_id"] == dataset_id
        assert payload["file_name"] == "insights_data.csv"
        assert "Executive Summary" in payload["summary"]
        assert payload["provider_used"] == "groq"

