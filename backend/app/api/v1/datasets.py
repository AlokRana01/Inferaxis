"""API route handlers for dataset ingestion, management, and quality profiling."""

from __future__ import annotations

import logging
import uuid
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.storage import FileSizeLimitExceededError
from app.schemas.dataset import (
    DatasetAIInsightsDTO,
    DatasetProfileResponseDTO,
    DatasetResponseDTO,
)
from app.services.dataset_service import (
    DatasetNotFoundError,
    DatasetService,
    WorkspaceNotFoundError,
)
from app.services.ingestor import (
    ColumnCountLimitExceededError,
    EmptyFileError,
    FileParsingError,
    IngestionError,
    RowCountLimitExceededError,
    UnsupportedFileFormatError,
)

logger = logging.getLogger("inferaxis.api.datasets")

router = APIRouter(prefix="/api/v1/datasets", tags=["datasets"])


def get_dataset_service() -> DatasetService:
    """Dependency provider for DatasetService."""
    return DatasetService()


@router.post(
    "/upload",
    response_model=DatasetResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and profile a tabular dataset (CSV or XLSX)",
)
async def upload_dataset(
    file: Annotated[
        UploadFile, File(description="Tabular file to upload (.csv or .xlsx)")
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
    service: Annotated[DatasetService, Depends(get_dataset_service)],
    workspace_id: Annotated[
        uuid.UUID | None, Form(description="Target Workspace UUID")
    ] = None,
    sheet_name: Annotated[
        str | None, Form(description="Target Excel worksheet name")
    ] = None,
) -> DatasetResponseDTO:
    """Ingest a CSV or XLSX dataset, generate an automated quality scorecard, and persist metadata."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must have a valid filename.",
        )

    try:
        dataset = await service.upload_and_process_dataset(
            db=db,
            file_stream=file.file,
            original_filename=file.filename,
            workspace_id=workspace_id,
            sheet_name=sheet_name,
        )
        return DatasetResponseDTO.model_validate(dataset)

    except UnsupportedFileFormatError as err:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=str(err),
        ) from err
    except EmptyFileError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err
    except FileSizeLimitExceededError as err:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(err),
        ) from err
    except (
        RowCountLimitExceededError,
        ColumnCountLimitExceededError,
        FileParsingError,
    ) as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(err),
        ) from err
    except WorkspaceNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err
    except IngestionError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Data ingestion error: {err}",
        ) from err
    except Exception as exc:
        logger.exception("Unexpected error processing dataset upload")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while processing the dataset.",
        ) from exc


@router.get(
    "/{dataset_id}",
    response_model=DatasetResponseDTO,
    summary="Retrieve dataset metadata by ID",
)
async def get_dataset(
    dataset_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    service: Annotated[DatasetService, Depends(get_dataset_service)],
    workspace_id: Annotated[
        uuid.UUID | None,
        Query(description="Optional Workspace UUID to enforce isolation"),
    ] = None,
) -> DatasetResponseDTO:
    """Fetch stored dataset entity and metadata."""
    try:
        dataset = await service.get_dataset_by_id(
            db, dataset_id, workspace_id=workspace_id
        )
        return DatasetResponseDTO.model_validate(dataset)
    except DatasetNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err


@router.get(
    "/{dataset_id}/profile",
    response_model=DatasetProfileResponseDTO,
    summary="Retrieve automated data quality scorecard and schema",
)
async def get_dataset_profile(
    dataset_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    service: Annotated[DatasetService, Depends(get_dataset_service)],
    workspace_id: Annotated[
        uuid.UUID | None,
        Query(description="Optional Workspace UUID to enforce isolation"),
    ] = None,
) -> DatasetProfileResponseDTO:
    """Fetch automated data quality profile and schema diagnostics for a dataset."""
    try:
        dataset = await service.get_dataset_by_id(
            db, dataset_id, workspace_id=workspace_id
        )
        return DatasetProfileResponseDTO(
            dataset_id=dataset.id,
            file_name=dataset.file_name,
            row_count=dataset.row_count or 0,
            col_count=dataset.col_count or 0,
            health_score=dataset.health_score or 0.0,
            schema_metadata=dataset.schema_metadata,
            profile_summary=dataset.profile_summary,
        )
    except DatasetNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err


@router.post(
    "/{dataset_id}/ai-insights",
    response_model=DatasetAIInsightsDTO,
    summary="Generate automated AI executive summary, quality alerts, and hypotheses",
)
async def generate_dataset_ai_insights(
    dataset_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    service: Annotated[DatasetService, Depends(get_dataset_service)],
    workspace_id: Annotated[
        uuid.UUID | None,
        Query(description="Optional Workspace UUID to enforce isolation"),
    ] = None,
) -> DatasetAIInsightsDTO:
    """Trigger LLM analysis over dataset profile to generate executive insights and suggested hypotheses."""
    try:
        return await service.generate_ai_insights(
            db=db,
            dataset_id=dataset_id,
            workspace_id=workspace_id,
        )
    except DatasetNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err
    except Exception as err:
        logger.exception("AI insights generation failed for dataset '%s'", dataset_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate AI insights: {err}",
        ) from err

