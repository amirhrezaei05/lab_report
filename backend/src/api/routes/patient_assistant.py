import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.models.database import get_db
from src.models.processed_file import ProcessedFile
from src.models.patient_assistant import PatientAssistant
from src.schemas.patient_assistant import PatientAssistantResponse

from src.LLM.patient_assist import patient_assistant


router = APIRouter(
    prefix="/api/patient-assistant",
    tags=["Patient Assistant"],
)


@router.post(
    "/{processed_file_id}",
    response_model=PatientAssistantResponse,
)
def generate_patient_assistant(
    processed_file_id: int,
    db: Session = Depends(get_db),
):
    # --------------------------------------------------------
    # Find processed file
    # --------------------------------------------------------

    processed_file = (
        db.query(ProcessedFile)
        .filter(
            ProcessedFile.id == processed_file_id
        )
        .first()
    )

    if not processed_file:
        raise HTTPException(
            status_code=404,
            detail="Processed file not found",
        )

    # --------------------------------------------------------
    # Check whether patient assistant already exists
    # --------------------------------------------------------

    existing = (
        db.query(PatientAssistant)
        .filter(
            PatientAssistant.processed_file_id
            == processed_file_id
        )
        .first()
    )

    if existing:
        return json.loads(existing.response_json)

    # --------------------------------------------------------
    # Get normalized JSON
    # --------------------------------------------------------

    # IMPORTANT:
    # Change this according to the actual field name
    # in your ProcessedFile model.

    json_path = processed_file.file_path

    if not json_path:
        raise HTTPException(
            status_code=400,
            detail="Processed file does not contain a JSON path",
        )

    json_path = Path(json_path)

    if not json_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Processed JSON file not found",
        )

    # --------------------------------------------------------
    # Run Patient LLM
    # --------------------------------------------------------

    try:
        assistant_result = patient_assistant(
            str(json_path)
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Patient assistant failed: {str(exc)}",
        )

    # --------------------------------------------------------
    # Save result
    # --------------------------------------------------------

    assistant_record = PatientAssistant(
        processed_file_id=processed_file.id,
        user_id=processed_file.user_id,
        response_json=json.dumps(
            assistant_result,
            ensure_ascii=False,
        ),
    )

    db.add(assistant_record)
    db.commit()
    db.refresh(assistant_record)

    # --------------------------------------------------------
    # Return response
    # --------------------------------------------------------

    return assistant_result