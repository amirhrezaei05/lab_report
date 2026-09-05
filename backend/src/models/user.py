# src/models/user.py

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    documents = relationship(
        "Document",
        back_populates="user",
    )
    patient_assistants = relationship(
        "PatientAssistant",
        back_populates="user",
        cascade="all, delete-orphan",
    )