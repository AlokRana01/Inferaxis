"""AnalysisSession database model."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.agent_step import AgentStep
    from app.models.analysis_report import AnalysisReport
    from app.models.dataset import Dataset


class AnalysisSession(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """An analytical session tracking agent investigation lifecycle for a user query."""

    __tablename__ = "analysis_sessions"

    dataset_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_query: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="PENDING",
        index=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    dataset: Mapped["Dataset"] = relationship(
        "Dataset", back_populates="analysis_sessions"
    )
    agent_steps: Mapped[list["AgentStep"]] = relationship(
        "AgentStep",
        back_populates="session",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="AgentStep.step_number",
        lazy="selectin",
    )
    analysis_reports: Mapped[list["AnalysisReport"]] = relationship(
        "AnalysisReport",
        back_populates="session",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<AnalysisSession(id={self.id}, status='{self.status}')>"
