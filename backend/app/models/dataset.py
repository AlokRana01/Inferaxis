"""Dataset metadata database model."""

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, BigInteger, Float, ForeignKey, Integer, String, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.analysis_session import AnalysisSession
    from app.models.workspace import Workspace


class Dataset(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Dataset stores structured metadata and storage references for tabular files."""

    __tablename__ = "datasets"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    row_count: Mapped[int | None] = mapped_column(Integer, nullable=True, default=0)
    col_count: Mapped[int | None] = mapped_column(Integer, nullable=True, default=0)
    health_score: Mapped[float | None] = mapped_column(
        Float, nullable=True, default=0.0
    )
    schema_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
    )
    profile_summary: Mapped[dict[str, Any] | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
    )

    # Relationships
    workspace: Mapped["Workspace"] = relationship(
        "Workspace", back_populates="datasets"
    )
    analysis_sessions: Mapped[list["AnalysisSession"]] = relationship(
        "AnalysisSession",
        back_populates="dataset",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Dataset(id={self.id}, file_name='{self.file_name}', rows={self.row_count}, cols={self.col_count})>"
