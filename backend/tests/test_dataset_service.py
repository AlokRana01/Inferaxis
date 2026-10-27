"""Integration tests for DatasetService orchestrating storage, ingestion, and database layer."""

import io
import uuid
from pathlib import Path

import pytest
from app.core.storage import LocalStorageService
from app.models.dataset import Dataset
from app.models.workspace import Workspace
from app.services.dataset_service import DatasetNotFoundError, DatasetService
from app.services.ingestor import EmptyFileError, UnsupportedFileFormatError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture
def test_storage(tmp_path: Path) -> LocalStorageService:
    return LocalStorageService(base_path=tmp_path / "service_storage")


@pytest.fixture
def dataset_service(test_storage: LocalStorageService) -> DatasetService:
    return DatasetService(storage_service=test_storage)


@pytest.mark.asyncio
async def test_upload_and_process_csv_success(
    db_session: AsyncSession,
    dataset_service: DatasetService,
    test_storage: LocalStorageService,
):
    """Verify full end-to-end flow: stream file, ingest, profile, and persist to database."""
    # 1. Create a workspace
    workspace = Workspace(name="Data Science Lab", owner_id="user_test_99")
    db_session.add(workspace)
    await db_session.flush()

    csv_content = (
        b"product_id,product_name,price,is_available\n"
        b"101,Widget Alpha,24.99,true\n"
        b"102,Widget Beta,49.50,false\n"
        b"103,Widget Gamma,9.99,true\n"
    )
    stream = io.BytesIO(csv_content)

    dataset = await dataset_service.upload_and_process_dataset(
        db=db_session,
        file_stream=stream,
        original_filename="products.csv",
        workspace_id=workspace.id,
    )

    assert dataset.id is not None
    assert dataset.workspace_id == workspace.id
    assert dataset.file_name == "products.csv"
    assert dataset.row_count == 3
    assert dataset.col_count == 4
    assert dataset.health_score > 80.0
    assert dataset.schema_metadata is not None
    assert dataset.schema_metadata["delimiter"] == ","
    assert dataset.profile_summary is not None
    assert "health_breakdown" in dataset.profile_summary

    # Verify file stored on disk via relative path
    assert test_storage.file_exists(dataset.file_path) is True
    assert not Path(dataset.file_path).is_absolute()


@pytest.mark.asyncio
async def test_failure_cleanup_and_rollback(
    db_session: AsyncSession,
    dataset_service: DatasetService,
    test_storage: LocalStorageService,
):
    """Verify that if ingestion fails, the temporary/stored file is cleaned up and DB is rolled back."""
    # Empty file triggers EmptyFileError
    empty_stream = io.BytesIO(b"")

    with pytest.raises(EmptyFileError):
        await dataset_service.upload_and_process_dataset(
            db=db_session,
            file_stream=empty_stream,
            original_filename="corrupted.csv",
        )

    # Assert no orphaned files in datasets directory
    datasets_files = list(test_storage.datasets_dir.glob("*"))
    assert len(datasets_files) == 0

    # Assert no dataset records in database
    query = select(Dataset)
    result = await db_session.execute(query)
    assert len(result.scalars().all()) == 0


@pytest.mark.asyncio
async def test_unsupported_format_rejection(
    db_session: AsyncSession,
    dataset_service: DatasetService,
    test_storage: LocalStorageService,
):
    """Verify rejecting unsupported file formats."""
    stream = io.BytesIO(b"some binary payload")
    with pytest.raises(UnsupportedFileFormatError):
        await dataset_service.upload_and_process_dataset(
            db=db_session,
            file_stream=stream,
            original_filename="document.pdf",
        )


@pytest.mark.asyncio
async def test_get_dataset_by_id(
    db_session: AsyncSession, dataset_service: DatasetService
):
    """Verify fetching dataset by UUID and raising DatasetNotFoundError on missing ID."""
    stream = io.BytesIO(b"id,val\n1,10\n")
    dataset = await dataset_service.upload_and_process_dataset(
        db=db_session,
        file_stream=stream,
        original_filename="simple.csv",
    )

    found = await dataset_service.get_dataset_by_id(db_session, dataset.id)
    assert found.id == dataset.id

    # Verify workspace isolation scoping
    other_workspace_id = uuid.uuid4()
    with pytest.raises(DatasetNotFoundError):
        await dataset_service.get_dataset_by_id(
            db_session, dataset.id, workspace_id=other_workspace_id
        )

    # Scoped with correct workspace succeeds
    same_ws = await dataset_service.get_dataset_by_id(
        db_session, dataset.id, workspace_id=dataset.workspace_id
    )
    assert same_ws.id == dataset.id

    with pytest.raises(DatasetNotFoundError):
        await dataset_service.get_dataset_by_id(db_session, uuid.uuid4())
