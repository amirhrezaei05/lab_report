import sys
import json
import urllib.request
import urllib.error
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

API_KEY = Path.home().joinpath("API_key.txt").read_text().strip()

DEFAULT_MODEL = "gemini-2.5-flash"


# ============================================================
# Normalization Prompt
# ============================================================

PROMPT = """
You are a medical laboratory report data normalization system.

You will receive raw OCR text from a medical laboratory report.

Your task is to convert the OCR text into a structured JSON object.

IMPORTANT RULES:

1. Preserve all information present in the OCR.
2. Do NOT diagnose the patient.
3. Do NOT interpret medical significance.
4. Do NOT decide whether a result is normal or abnormal.
5. Do NOT add information that is not present.
6. Do NOT guess missing information.
7. Use null for missing information.
8. Preserve the original test names.
9. Preserve Persian test names when present.
10. Preserve units exactly as they appear.
11. Preserve reference ranges.
12. Separate result values from units.
13. Preserve qualitative results such as Positive, Negative, Moderate, etc.
14. Preserve laboratory departments/sections.
15. Preserve blood group and Rh factor.
16. Preserve dates exactly as they appear.
17. Do not convert Persian dates to Gregorian dates.
18. Do not silently correct OCR errors.
19. Keep the original OCR fragment for each test in "original_text".
20. Return ONLY valid JSON.
21. Do NOT use Markdown.
22. Do NOT provide explanations.

Use this JSON structure:

{
  "document_type": "lab_report",

  "laboratory": {
    "name": null,
    "address": null,
    "telephone": null,
    "fax": null
  },

  "patient": {
    "name": null,
    "age": null,
    "gender": null
  },

  "report": {
    "date": null,
    "physician": null,
    "accession_number": null
  },

  "sections": {
    "blood_biochemistry": [],
    "hematology": [],
    "urine_analysis": [],
    "other": []
  },

  "blood_type": {
    "abo": null,
    "rh": null
  },

  "additional_information": []
}

Each laboratory test should use:

{
  "test_name": null,
  "test_name_fa": null,
  "result": null,
  "unit": null,
  "reference_range": {
    "low": null,
    "high": null,
    "text": null
  },
  "original_text": null
}

If a reference range cannot be represented numerically,
preserve it in "text".

For example:

">30"

should become:

{
  "low": null,
  "high": null,
  "text": ">30"
}

Do not invent values.

RAW OCR TEXT:
"""


# ============================================================
# Gemini Normalization
# ============================================================

def normalize(ocr_json_path: str, model: str = DEFAULT_MODEL) -> dict:

    path = Path(ocr_json_path)

    if not path.exists():
        raise FileNotFoundError(
            f"JSON file does not exist: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Path is not a file: {path}"
        )

    # --------------------------------------------------------
    # Read raw OCR JSON
    # --------------------------------------------------------

    with open(path, "r", encoding="utf-8") as f:
        ocr_data = json.load(f)

    if "text" not in ocr_data:
        raise ValueError(
            "OCR JSON does not contain a 'text' field."
        )

    ocr_text = ocr_data["text"]

    if not ocr_text.strip():
        raise ValueError(
            "OCR JSON contains an empty 'text' field."
        )

    # --------------------------------------------------------
    # Build prompt
    # --------------------------------------------------------

    prompt = PROMPT + "\n" + ocr_text

    # --------------------------------------------------------
    # Vertex AI request
    # --------------------------------------------------------

    body = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0,
            "responseMimeType": "application/json"
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

    # --------------------------------------------------------
    # Send request
    # --------------------------------------------------------

    try:

        with urllib.request.urlopen(
            request,
            timeout=180
        ) as response:

            result = json.load(response)

    except urllib.error.HTTPError as exc:

        error_body = exc.read().decode(
            "utf-8",
            errors="replace"
        )

        raise RuntimeError(
            f"Gemini API error {exc.code}: "
            f"{error_body[:1000]}"
        ) from exc

    except urllib.error.URLError as exc:

        raise RuntimeError(
            f"Could not connect to Gemini API: {exc}"
        ) from exc

    # --------------------------------------------------------
    # Extract Gemini response
    # --------------------------------------------------------

    candidates = result.get("candidates", [])

    if not candidates:
        raise RuntimeError(
            "Gemini returned no candidates:\n"
            + json.dumps(
                result,
                indent=2
            )[:2000]
        )

    parts = candidates[0].get(
        "content",
        {}
    ).get(
        "parts",
        []
    )

    text_parts = []

    for part in parts:

        text = part.get("text")

        if text:
            text_parts.append(text)

    text = "".join(text_parts).strip()

    if not text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    # --------------------------------------------------------
    # Convert Gemini JSON string → Python dict
    # --------------------------------------------------------

    try:

        structured_data = json.loads(text)

    except json.JSONDecodeError as exc:

        raise RuntimeError(
            "Gemini returned invalid JSON:\n"
            + text[:2000]
        ) from exc

    # --------------------------------------------------------
    # Add processing metadata
    # --------------------------------------------------------

    structured_data["_metadata"] = {
        "source_ocr_file": path.name,
        "model": model
    }

    return structured_data


# ============================================================
# CLI
# ============================================================

def main():

    if len(sys.argv) < 2:

        print(
            "Usage: python3 normalizer.py "
            "<ocr_json_path> [model]"
        )

        sys.exit(1)

    json_path = sys.argv[1]

    model = (
        sys.argv[2]
        if len(sys.argv) > 2
        else DEFAULT_MODEL
    )

    result = normalize(
        json_path,
        model
    )

    # --------------------------------------------------------
    # Output filename
    # --------------------------------------------------------

    output_path = Path(json_path).with_name(
        Path(json_path).stem + "_normalized.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            result,
            f,
            ensure_ascii=False,
            indent=2
        )

    print("Normalization completed.")
    print(f"JSON saved to: {output_path}")


if __name__ == "__main__":
    main()