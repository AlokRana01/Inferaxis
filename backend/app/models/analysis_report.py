"""AnalysisReport database model storing finalized analytical synthesis."""

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import ForeignKey, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.analysis_session import AnalysisSession


class AnalysisReport(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """The synthesized analytical findings, evidence, chart specs, and recommendations."""

    __tablename__ = "analysis_reports"

    session_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("analysis_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
    pdf_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    # Relationships
    session: Mapped["AnalysisSession"] = relationship(
        "AnalysisSession", back_populates="analysis_reports"
    )

    def __repr__(self) -> str:
        return f"<AnalysisReport(id={self.id}, session_id={self.session_id})>"
