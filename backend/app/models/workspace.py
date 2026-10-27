"""Workspace database model."""

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.dataset import Dataset


class Workspace(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Workspaces logically group datasets and analytical sessions."""

    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    owner_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    # Relationships
    datasets: Mapped[list["Dataset"]] = relationship(
        "Dataset",
        back_populates="workspace",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Workspace(id={self.id}, name='{self.name}')>"
