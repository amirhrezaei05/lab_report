from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.models.database import get_db
from src.models.document import Document
from src.models.processed_file import ProcessedFile

from src.ocr.preprocessing.loader import load_image
from src.ocr.preprocessing.pdf import pdf_to_images
from src.ocr.preprocessing.pipeline import preprocess


router = APIRouter(
    prefix="/api/ocr",
    tags=["OCR Preprocessing"],
)


PROCESSED_DIR = Path("data/processed")


ALLOWED_IMAGES = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tif",
    ".tiff",
    ".webp",
}


@router.post(
    "/preprocess/{document_id}",
)
def preprocess_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    # -------------------------
    # Get document
    # -------------------------

    document = db.get(Document, document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    input_path = Path(document.original_path)

    if not input_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Original file not found.",
        )

    # -------------------------
    # Create output directory
    # -------------------------

    output_dir = (
        PROCESSED_DIR /
        str(document.id)
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    processed_files = []

    # =====================================================
    # IMAGE
    # =====================================================

    if input_path.suffix.lower() in ALLOWED_IMAGES:

        image = load_image(input_path)

        processed = preprocess(
            image,
            grayscale=True,
            scale=1.0,
            contrast=1.2,
            apply_denoise=True,
            denoise_kernel=3,
        )

        output_path = (
            output_dir /
            "page_001.png"
        )

        processed.save(output_path)

        processed_file = ProcessedFile(
            document_id=document.id,
            file_path=str(output_path),
            page_number=1,
        )

        db.add(processed_file)

        processed_files.append(
            processed_file
        )

    # =====================================================
    # PDF
    # =====================================================

    elif input_path.suffix.lower() == ".pdf":

        page_images = pdf_to_images(
            input_path,
            output_dir,
            dpi=300,
        )

        for page_number, page_path in enumerate(
            page_images,
            start=1,
        ):

            image = load_image(page_path)

            processed = preprocess(
                image,
                grayscale=True,
                scale=1.0,
                contrast=1.2,
                apply_denoise=True,
                denoise_kernel=3,
            )

            output_path = (
                output_dir /
                f"page_{page_number:03d}.png"
            )

            processed.save(output_path)

            processed_file = ProcessedFile(
                document_id=document.id,
                file_path=str(output_path),
                page_number=page_number,
            )

            db.add(processed_file)

            processed_files.append(
                processed_file
            )

    else:

        raise HTTPException(
            status_code=400,
            detail="Unsupported document type.",
        )

    # -------------------------
    # Update document
    # -------------------------

    document.status = "preprocessed"

    db.commit()

    return {
        "document_id": document.id,
        "status": document.status,
        "pages": len(processed_files),
        "processed_files": [
            {
                "id": item.id,
                "page_number": item.page_number,
                "file_path": item.file_path,
            }
            for item in processed_files
        ],
    }