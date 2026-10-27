"""Pydantic v2 schemas for Dataset ingestion and profiling API requests and responses."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ColumnSchemaDTO(BaseModel):
    """Pydantic representation of a column's schema."""

    model_config = ConfigDict(from_attributes=True)

    name: str
    original_name: str
    dtype: str
    inferred_type: str
    nullable: bool


class DatasetSchemaMetadataDTO(BaseModel):
    """Pydantic representation of dataset import schema metadata."""

    model_config = ConfigDict(from_attributes=True)

    file_name: str
    file_size_bytes: int
    mime_type: str
    row_count: int
    col_count: int
    encoding: str | None = None
    delimiter: str | None = None
    sheets: list[str] = Field(default_factory=list)
    selected_sheet: str | None = None
    columns: list[ColumnSchemaDTO] = Field(default_factory=list)
    import_warnings: list[str] = Field(default_factory=list)


class DatasetResponseDTO(BaseModel):
    """Standardized API response for a persisted dataset."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workspace_id: uuid.UUID
    file_name: str
    file_size_bytes: int | None
    mime_type: str | None
    row_count: int
    col_count: int
    health_score: float
    schema_metadata: dict[str, Any] | None = None
    profile_summary: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class DatasetProfileResponseDTO(BaseModel):
    """API response specifically returning the data quality scorecard and schema."""

    model_config = ConfigDict(from_attributes=True)

    dataset_id: uuid.UUID
    file_name: str
    row_count: int
    col_count: int
    health_score: float
    schema_metadata: dict[str, Any] | None = None
    profile_summary: dict[str, Any] | None = None
