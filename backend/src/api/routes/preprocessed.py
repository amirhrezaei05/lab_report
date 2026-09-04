from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from PIL import Image

from src.ocr.preprocessing.loader import load_image
from src.ocr.preprocessing.pdf import pdf_to_images
from src.ocr.preprocessing.pipeline import preprocess


router = APIRouter(
    prefix="/api/ocr",
    tags=["OCR Preprocessing"],
)


ALLOWED_IMAGES = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tif",
    ".tiff",
    ".webp",
}

ALLOWED_EXTENSIONS = ALLOWED_IMAGES | {".pdf"}


@router.post("/preprocess")
async def preprocess_document(
    file: UploadFile = File(...),
):
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

    with TemporaryDirectory() as temp_dir:

        temp_dir = Path(temp_dir)

        input_path = temp_dir / file.filename

        content = await file.read()
        input_path.write_bytes(content)

        output_dir = temp_dir / "processed"
        output_dir.mkdir()

        # -------------------------
        # IMAGE
        # -------------------------
        if extension in ALLOWED_IMAGES:

            image = load_image(input_path)

            processed = preprocess(
                image,
                grayscale=True,
                scale=1.0,
                contrast=1.2,
                apply_denoise=True,
                denoise_kernel=3,
            )

            output_path = output_dir / "preprocessed.png"

            processed.save(output_path)

            return FileResponse(
                path=output_path,
                media_type="image/png",
                filename="preprocessed.png",
            )

        # -------------------------
        # PDF
        # -------------------------
        if extension == ".pdf":

            page_images = pdf_to_images(
                input_path,
                output_dir,
                dpi=300,
            )

            processed_paths = []

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

                processed_path = (
                    output_dir
                    / f"preprocessed_page_{page_number:03d}.png"
                )

                processed.save(processed_path)

                processed_paths.append(processed_path)

            # For now return first page.
            # Later we will return all pages properly.
            if not processed_paths:
                raise HTTPException(
                    status_code=400,
                    detail="PDF contains no pages.",
                )

            return FileResponse(
                path=processed_paths[0],
                media_type="image/png",
                filename="preprocessed_page_001.png",
            )