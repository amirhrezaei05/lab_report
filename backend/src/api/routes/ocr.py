
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.models.database import get_db
from src.models.document import Document
from src.models.processed_file import ProcessedFile
from src.models.ocr_result import OCRResult

from src.ocr.engine.gemini_ocr import ocr
from src.ocr.engine.gemini_normalizer import normalize


router = APIRouter(
    prefix="/api/ocr",
    tags=["OCR"],
)


# ---------------------------------------------------------
# POST /api/ocr/{document_id}
# ---------------------------------------------------------

@router.post("/{document_id}")
def process_ocr(
    document_id: int,
    db: Session = Depends(get_db),
):

    # -----------------------------------------------------
    # 1. Find document
    # -----------------------------------------------------

    document = db.get(Document, document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    # -----------------------------------------------------
    # 2. Find preprocessed files
    # -----------------------------------------------------

    processed_files = (
        db.query(ProcessedFile)
        .filter(
            ProcessedFile.document_id == document_id
        )
        .order_by(
            ProcessedFile.page_number
        )
        .all()
    )

    if not processed_files:
        raise HTTPException(
            status_code=400,
            detail="Document has not been preprocessed",
        )

    # -----------------------------------------------------
    # 3. Run Gemini OCR
    # -----------------------------------------------------

    pages = []

    for processed_file in processed_files:

        image_path = Path(
            processed_file.file_path
        )

        if not image_path.exists():
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Processed image not found: "
                    f"{image_path}"
                ),
            )

        # Your actual function is:
        # ocr(path)

        ocr_output = ocr(
            str(image_path)
        )

        pages.append(
            {
                "page_number": processed_file.page_number,
                "ocr": ocr_output,
            }
        )

    # -----------------------------------------------------
    # 4. Gemini normalization
    # -----------------------------------------------------

    # Your actual function is:
    # normalize(...)

    ocr_output = ocr(str(image_path))

    normalized_result = normalize(ocr_output)
    # -----------------------------------------------------
    # 5. Save OCR / normalized result
    # -----------------------------------------------------

    ocr_result = OCRResult(
        document_id=document.id,
        result=normalized_result,
    )

    db.add(ocr_result)

    # -----------------------------------------------------
    # 6. Update document status
    # -----------------------------------------------------

    document.status = "ocr_completed"

    db.commit()
    db.refresh(ocr_result)

    # -----------------------------------------------------
    # 7. Return
    # -----------------------------------------------------

    return {
        "id": ocr_result.id,
        "document_id": document.id,
        "status": document.status,
        "result": ocr_result.result,
        "created_at": ocr_result.created_at,
    }


# ---------------------------------------------------------
# GET /api/ocr/{document_id}
# ---------------------------------------------------------

@router.get("/{document_id}")
def get_ocr(
    document_id: int,
    db: Session = Depends(get_db),
):

    # -----------------------------------------------------
    # 1. Check document
    # -----------------------------------------------------

    document = db.get(
        Document,
        document_id
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    # -----------------------------------------------------
    # 2. Find OCR result
    # -----------------------------------------------------

    ocr_result = (
        db.query(OCRResult)
        .filter(
            OCRResult.document_id == document_id
        )
        .order_by(
            OCRResult.created_at.desc()
        )
        .first()
    )

    if ocr_result is None:
        raise HTTPException(
            status_code=404,
            detail="OCR result not found",
        )

    # -----------------------------------------------------
    # 3. Return result
    # -----------------------------------------------------

    return {
        "id": ocr_result.id,
        "document_id": ocr_result.document_id,
        "status": document.status,
        "result": ocr_result.result,
        "created_at": ocr_result.created_at,
    }

