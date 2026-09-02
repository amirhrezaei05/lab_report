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
# Patient Assistant Prompt
# ============================================================

PROMPT = """
You are a patient-facing medical laboratory report assistant.

Your job is to explain a laboratory report to a patient in simple,
clear, understandable language.

You are NOT a doctor and you must NOT diagnose diseases.

The input is a STRUCTURED laboratory report JSON.

============================================================
CORE RULES
============================================================
0. the output language is Farsi (فارسی)

1. Use ONLY information contained in the provided laboratory report.

2. Do NOT invent patient information, test results, symptoms,
   diagnoses, medications, medical history, or other facts.

3. Explain laboratory tests in language understandable to a
   non-medical person.

4. You may explain what a test generally measures.

5. You may compare a result with the reference range provided
   in the laboratory report.

6. If a result is outside the provided reference range, explain
   that it is outside that laboratory's stated range.

7. Do NOT diagnose a disease based only on a laboratory result.

8. Do NOT claim that an abnormal result definitely means a
   particular disease.

9. Do NOT recommend starting, stopping, or changing medication.

10. Do NOT provide specific treatment plans.

11. Do NOT invent a reference range when the report does not
    provide one.

12. Do NOT use external medical knowledge to override the
    laboratory's reference range.

13. If information is missing, explicitly say that it is not
    available in the report.

14. If a result is ambiguous or unclear, say so rather than
    guessing.

15. Distinguish between:
       - within the provided reference range
       - below the provided reference range
       - above the provided reference range
       - qualitative result
       - unable to determine

16. Avoid unnecessarily alarming language.

17. Avoid falsely reassuring language.

18. Explain uncertainty when appropriate.

19. If a result may warrant discussion with a healthcare
    professional, say:
    "You may want to discuss this result with your doctor."

20. Do not tell the patient that they definitely have or do not
    have a disease.

============================================================
PATIENT-FRIENDLY LANGUAGE
============================================================

Use simple language.

For example:

Instead of:
"Creatinine is a marker of renal function."

Prefer:
"Creatinine is a substance measured in the blood that can provide
information about how the kidneys are working."

Do not overload the patient with medical terminology.

If a medical term is necessary, explain it immediately.

============================================================
IMPORTANT DISTINCTION
============================================================

There are THREE different things:

A) What the test measures
B) Whether the result is inside the laboratory's reference range
C) What the result means for the patient's health

You can explain A and B.

Be cautious with C.

Do NOT make a diagnosis from the laboratory result alone.

============================================================
OUTPUT
============================================================

Return ONLY valid JSON.

Use exactly this structure:

{
  "summary": "",
  "results": [
    {
      "test_name": "",
      "result": null,
      "unit": null,
      "reference_range": "",
      "status": "",
      "explanation": ""
      , is_clinically_poblematic: false
    }
  ],
  "important_points": [],
  "questions_for_doctor": [],
  "safety_note": ""
  ,"dietry_paln" : ""
  , pyhsical_exccersice_plan : ""
}

============================================================
FIELD RULES
============================================================

summary:
Give a short overall explanation of the report.

results:
Explain the individual laboratory results that are present.

test_name:
Use the test name from the report.

result:
Preserve the actual reported result.

unit:
Preserve the reported unit.

reference_range:
Preserve the reference range from the report.

status:
Use ONLY one of:

"within_range"
"below_range"
"above_range"
"qualitative"
"unable_to_determine"

explanation:
Give a short patient-friendly explanation.

important_points:
Include only results that deserve attention because they are
outside the provided reference range or are otherwise notable
from the report.

Do NOT diagnose the cause.

questions_for_doctor:
Provide reasonable questions the patient could ask their doctor
when appropriate.

Do not create questions for every normal result.

safety_note:
Include a short statement explaining that the report should be
interpreted together with the patient's symptoms, history, and
clinical examination.

============================================================
INPUT
============================================================

STRUCTURED LAB REPORT:

"""


# ============================================================
# Gemini Patient Assistant
# ============================================================

def patient_assistant(
    json_path: str,
    model: str = DEFAULT_MODEL
) -> dict:

    path = Path(json_path)

    if not path.exists():
        raise FileNotFoundError(
            f"JSON file does not exist: {path}"
        )

    if not path.is_file():
        raise ValueError(
            f"Path is not a file: {path}"
        )

    # --------------------------------------------------------
    # Read structured JSON
    # --------------------------------------------------------

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        structured_data = json.load(f)

    # --------------------------------------------------------
    # Convert structured JSON to text for Gemini
    # --------------------------------------------------------

    report_json = json.dumps(
        structured_data,
        ensure_ascii=False,
        indent=2
    )

    prompt = PROMPT + report_json

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
            "temperature": 0.2,
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
    # Extract response
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
    # Parse JSON
    # --------------------------------------------------------

    try:

        assistant_response = json.loads(text)

    except json.JSONDecodeError as exc:

        raise RuntimeError(
            "Gemini returned invalid JSON:\n"
            + text[:2000]
        ) from exc

    return assistant_response


# ============================================================
# CLI
# ============================================================

def main():

    if len(sys.argv) < 2:

        print(
            "Usage: python3 patient_assistant.py "
            "<normalized_json> [model]"
        )

        sys.exit(1)

    json_path = sys.argv[1]

    model = (
        sys.argv[2]
        if len(sys.argv) > 2
        else DEFAULT_MODEL
    )

    result = patient_assistant(
        json_path,
        model
    )

    # --------------------------------------------------------
    # Output filename
    # --------------------------------------------------------

    output_path = Path(json_path).with_name(
        Path(json_path).stem + "_patient.json"
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

    print("Patient assistant completed.")
    print(f"JSON saved to: {output_path}")


if __name__ == "__main__":
    main()