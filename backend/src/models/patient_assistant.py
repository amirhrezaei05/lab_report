from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship

from src.models.base import Base


class PatientAssistant(Base):
    __tablename__ = "patient_assistants"

    id = Column(Integer, primary_key=True, index=True)

    processed_file_id = Column(
        Integer,
        ForeignKey("processed_files.id"),
        nullable=False,
        unique=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    response_json = Column(
        Text,
        nullable=False,
    )

    processed_file = relationship(
        "ProcessedFile",
        back_populates="patient_assistant",
    )

    user = relationship(
        "User",
        back_populates="patient_assistants",
    )