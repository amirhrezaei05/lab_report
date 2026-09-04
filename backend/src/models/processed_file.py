# src/models/processed_file.py

from datetime import datetime

from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class ProcessedFile(Base):
    __tablename__ = "processed_files"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    document_id: Mapped[int] = mapped_column(
        ForeignKey("documents.id"),
        nullable=False,
    )

    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    page_number: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    document = relationship(
        "Document",
        back_populates="processed_files",
    )