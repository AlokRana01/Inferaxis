"""Dataset management service orchestrating storage, ingestion, profiling, and database persistence."""

from __future__ import annotations

import logging
import uuid
from pathlib import Path
from typing import BinaryIO

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.storage import LocalStorageService, get_storage_service
from app.models.dataset import Dataset
from app.models.workspace import Workspace
from app.schemas.dataset import DatasetAIInsightsDTO
from app.services.ingestor import (
    DataIngestor,
    UnsupportedFileFormatError,
)
from app.services.llm_router import LLMRouter, LLMTaskType, get_llm_router
from app.services.profiler import DataQualityProfiler

logger = logging.getLogger("inferaxis.dataset_service")


class DatasetServiceError(Exception):
    """Base exception for dataset service operations."""


class WorkspaceNotFoundError(DatasetServiceError):
    """Raised when the specified workspace does not exist."""


class DatasetNotFoundError(DatasetServiceError):
    """Raised when a dataset ID is not found in database."""


class DatasetService:
    """Coordinates tabular file upload, deterministic ingestion, profiling, and persistence."""

    def __init__(
        self,
        storage_service: LocalStorageService | None = None,
        ingestor: DataIngestor | None = None,
        profiler: DataQualityProfiler | None = None,
    ) -> None:
        self.storage = storage_service or get_storage_service()
        self.ingestor = ingestor or DataIngestor()
        self.profiler = profiler or DataQualityProfiler()
        self.settings = get_settings()

    async def get_or_create_default_workspace(self, db: AsyncSession) -> Workspace:
        """Retrieve existing default workspace or initialize a development workspace."""
        query = select(Workspace).limit(1)
        result = await db.execute(query)
        workspace = result.scalars().first()
        if not workspace:
            workspace = Workspace(
                name="Default Workspace",
                owner_id="dev_user",
            )
            db.add(workspace)
            await db.flush()
        return workspace

    async def upload_and_process_dataset(
        self,
        db: AsyncSession,
        file_stream: BinaryIO,
        original_filename: str,
        workspace_id: uuid.UUID | None = None,
        sheet_name: str | None = None,
    ) -> Dataset:
        """Stream tabular file, run deterministic ingestion and quality profiling, and commit to database.

        If ingestion, profiling, or database commit fails, any written files are cleaned up.

        Args:
            db: Active async database session.
            file_stream: Readable binary file stream.
            original_filename: User-supplied name of uploaded file.
            workspace_id: Target workspace ID. If omitted, uses default workspace.
            sheet_name: Optional target worksheet for Excel files.

        Returns:
            Newly created and persisted Dataset model instance.

        Raises:
            WorkspaceNotFoundError: If provided workspace_id does not exist.
            IngestionError: If file validation or parsing fails.
        """
        # Validate or resolve target workspace
        if workspace_id:
            query = select(Workspace).where(Workspace.id == workspace_id)
            result = await db.execute(query)
            workspace = result.scalars().first()
            if not workspace:
                raise WorkspaceNotFoundError(
                    f"Workspace with id '{workspace_id}' not found"
                )
        else:
            workspace = await self.get_or_create_default_workspace(db)

        # Sanitize extension
        suffix = Path(original_filename).suffix.lower()
        if suffix not in DataIngestor.SUPPORTED_EXTENSIONS:
            raise UnsupportedFileFormatError(
                f"Unsupported file format '{suffix}'. Allowed: {', '.join(sorted(DataIngestor.SUPPORTED_EXTENSIONS))}"
            )

        dataset_id = uuid.uuid4()
        relative_path = f"datasets/{dataset_id}{suffix}"
        saved_relative_path: str | None = None

        try:
            # 1. Stream file to storage
            saved_relative_path, written_bytes = self.storage.save_stream(
                stream=file_stream,
                relative_path=relative_path,
                max_size_bytes=self.settings.MAX_UPLOAD_SIZE_BYTES,
            )

            # 2. Ingest file from storage
            absolute_path = self.storage.get_path(saved_relative_path)
            ingestion_result = self.ingestor.ingest_file(
                file_path=absolute_path,
                original_filename=original_filename,
                sheet_name=sheet_name,
            )

            # 3. Profile DataFrame deterministically
            quality_profile = self.profiler.profile_dataframe(
                ingestion_result.dataframe
            )

            # 4. Construct Dataset entity with schema and profiling metadata
            dataset = Dataset(
                id=dataset_id,
                workspace_id=workspace.id,
                file_name=original_filename,
                file_path=saved_relative_path,
                file_size_bytes=written_bytes,
                mime_type=ingestion_result.mime_type,
                row_count=ingestion_result.row_count,
                col_count=ingestion_result.col_count,
                health_score=quality_profile.health_score,
                schema_metadata=ingestion_result.to_schema_metadata(),
                profile_summary=quality_profile.to_dict(),
            )

            db.add(dataset)
            await db.commit()
            await db.refresh(dataset)
            return dataset

        except Exception:
            # Clean up stored file if database commit or ingestion fails
            if saved_relative_path:
                logger.info(
                    "Cleaning up stored file %s due to ingestion failure",
                    saved_relative_path,
                )
                self.storage.delete_file(saved_relative_path)
            await db.rollback()
            raise

    async def get_dataset_by_id(
        self,
        db: AsyncSession,
        dataset_id: uuid.UUID,
        workspace_id: uuid.UUID | None = None,
    ) -> Dataset:
        """Fetch dataset entity by primary key, optionally verifying workspace ownership."""
        query = select(Dataset).where(Dataset.id == dataset_id)
        if workspace_id is not None:
            query = query.where(Dataset.workspace_id == workspace_id)

        result = await db.execute(query)
        dataset = result.scalars().first()
        if not dataset:
            if workspace_id is not None:
                raise DatasetNotFoundError(
                    f"Dataset '{dataset_id}' not found in workspace '{workspace_id}'"
                )
            raise DatasetNotFoundError(f"Dataset '{dataset_id}' not found")
        return dataset

    async def generate_ai_insights(
        self,
        db: AsyncSession,
        dataset_id: uuid.UUID,
        workspace_id: uuid.UUID | None = None,
        llm_router: LLMRouter | None = None,
    ) -> DatasetAIInsightsDTO:
        """Analyze dataset profile and metadata using LLM to generate executive insights, quality alerts, and hypotheses."""
        dataset = await self.get_dataset_by_id(
            db, dataset_id=dataset_id, workspace_id=workspace_id
        )
        router = llm_router or get_llm_router()

        schema = dataset.schema_metadata or {}
        columns = [str(col.get("name")) for col in schema.get("columns", [])]
        summary = dataset.profile_summary or {}

        prompt = (
            f"Dataset Name: {dataset.file_name}\n"
            f"Rows: {dataset.row_count}, Columns: {dataset.col_count}\n"
            f"Health Score: {dataset.health_score} / 100\n"
            f"Columns: {', '.join(columns)}\n"
            f"Data Summary: {summary.get('shape', {})}\n\n"
            "Analyze this dataset profile and provide:\n"
            "1. Executive Summary: 2-3 sentences explaining what this dataset contains and overall readiness.\n"
            "2. Quality Alerts: List any critical data quality warnings or missing value issues.\n"
            "3. Suggested Hypotheses: 3 clear, testable hypotheses for exploratory data analysis.\n"
            "4. Suggested Visualizations: 2-3 chart types with recommended axes.\n"
            "Format your answer cleanly with Markdown headings."
        )

        system_prompt = (
            "You are Inferaxis AI Data Intelligence Scientist. Provide concise, rigorous, "
            "evidence-based analytical assessment of dataset metadata."
        )

        ai_response = await router.complete(
            prompt=prompt,
            system_prompt=system_prompt,
            task_type=LLMTaskType.FAST,
        )

        return DatasetAIInsightsDTO(
            dataset_id=dataset.id,
            file_name=dataset.file_name,
            summary=ai_response,
            quality_alerts=[],
            suggested_hypotheses=[],
            suggested_visualizations=[],
            provider_used=router.settings.LLM_PROVIDER,
        )

