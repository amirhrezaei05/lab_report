import sys
import json
import base64
import mimetypes
import urllib.request
import urllib.error
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

API_KEY = Path.home().joinpath("API_key.txt").read_text().strip()

DEFAULT_MODEL = "gemini-2.5-flash"

PROMPT = """
You are performing OCR on a medical laboratory report.

Your task is ONLY to transcribe the document.

Rules:

1. Extract ALL visible text from the document.
2. Preserve the original wording exactly.
3. Preserve numbers, decimal points, units, reference ranges,
   dates, patient information, test names, abbreviations,
   symbols, punctuation, and special characters.
4. Do NOT correct spelling.
5. Do NOT translate anything.
6. Do NOT interpret medical information.
7. Do NOT infer missing or unclear values.
8. Do NOT invent text that is not visible.
9. Preserve the document's reading order.
10. For Persian/Arabic text, preserve the correct right-to-left
    reading order.
11. Preserve line breaks whenever they are meaningful.
12. Preserve table structure as much as possible using plain text.
13. Keep English and Persian text exactly as they appear.
14. If a character or value is genuinely unreadable, use [UNCLEAR]
    rather than guessing.
15. Return ONLY the OCR text.
16. Do not add explanations, summaries, or commentary.
"""


# ============================================================
# Utilities
# ============================================================

def mime_of(path: str) -> str:
    """
    Determine MIME type from file extension.
    """
    mime, _ = mimetypes.guess_type(path)

    if mime:
        return mime

    suffix = Path(path).suffix.lower()

    known_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".pdf": "application/pdf",
        ".tif": "image/tiff",
        ".tiff": "image/tiff",
    }

    return known_types.get(suffix, "application/octet-stream")


def encode_file(path: str) -> str:
    """
    Read a file and return base64 encoded content.
    """
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


# ============================================================
# Gemini OCR
# ============================================================

def ocr(path: str, model: str = DEFAULT_MODEL) -> dict:

    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"File does not exist: {path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    mime_type = mime_of(str(path))

    if mime_type == "application/octet-stream":
        raise ValueError(
            f"Unsupported or unknown file type: {path.suffix}"
        )

    encoded_file = encode_file(str(path))

    body = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "inlineData": {
                            "mimeType": mime_type,
                            "data": encoded_file,
                        }
                    },
                    {
                        "text": PROMPT
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0
        }
    }

    url = (
        "https://aiplatform.googleapis.com/v1/"
        "publishers/google/models/"
        f"{model}:generateContent"
    )

    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "x-goog-api-key": API_KEY,
            "content-type": "application/json",
        },
        method="POST",
    )

    try:

        with urllib.request.urlopen(request, timeout=180) as response:
            result = json.load(response)

    except urllib.error.HTTPError as exc:

        error_body = exc.read().decode("utf-8", errors="replace")

        raise RuntimeError(
            f"Gemini API error {exc.code}: {error_body[:1000]}"
        ) from exc

    except urllib.error.URLError as exc:

        raise RuntimeError(
            f"Could not connect to Gemini API: {exc}"
        ) from exc

    candidates = result.get("candidates", [])

    if not candidates:
        raise RuntimeError(
            "Gemini returned no candidates:\n"
            + json.dumps(result, indent=2)[:2000]
        )

    parts = candidates[0].get("content", {}).get("parts", [])

    text_parts = []

    for part in parts:
        text = part.get("text")

        if text:
            text_parts.append(text)

    text = "".join(text_parts).strip()

    if not text:
        raise RuntimeError(
            "Gemini returned an empty OCR result."
        )

    return {
        "document_type": "lab_report",
        "source_file": path.name,
        "mime_type": mime_type,
        "model": model,
        "text": text,
    }


# ============================================================
# CLI
# ============================================================

def main():

    if len(sys.argv) < 2:
        print("Usage: python3 gemini.py <image_path> [model]")
        sys.exit(1)

    path = sys.argv[1]

    model = (
        sys.argv[2]
        if len(sys.argv) > 2
        else DEFAULT_MODEL
    )

    result = ocr(path, model)

    # Create JSON filename next to the image
    output_path = Path(path).with_suffix(".json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            result,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(f"OCR completed.")
    print(f"JSON saved to: {output_path}")


if __name__ == "__main__":
    main()