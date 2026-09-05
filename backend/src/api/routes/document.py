from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from src.models.database import get_db
from src.models.document import Document
from src.models.user import User
from src.schemas.document import DocumentResponse


router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"],
)


UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tif",
    ".tiff",
    ".webp",
    ".pdf",
}


@router.post(
    "/",
    response_model=DocumentResponse,
)
async def create_document(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # -------------------------
    # Validate filename
    # -------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided.",
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {extension}",
        )

    # -------------------------
    # Check user
    # -------------------------

    user = db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found.",
        )

    # -------------------------
    # Create document
    # -------------------------

    document = Document(
        user_id=user_id,
        original_filename=file.filename,
        original_path="",
        document_type=extension.lstrip("."),
        status="uploaded",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    # -------------------------
    # Create document directory
    # -------------------------

    document_dir = UPLOAD_DIR / str(document.id)
    document_dir.mkdir(parents=True, exist_ok=True)

    safe_filename = Path(file.filename).name

    file_path = document_dir / safe_filename

    # -------------------------
    # Save uploaded file
    # -------------------------

    content = await file.read()
    file_path.write_bytes(content)

    # -------------------------
    # Update database
    # -------------------------

    document.original_path = str(file_path)

    db.commit()
    db.refresh(document)

    return document


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = db.get(Document, document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    return document