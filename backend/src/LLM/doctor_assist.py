```python
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
# Doctor Assistant Prompt
# ============================================================

PROMPT = """
You are a physician-facing clinical decision-support assistant
for a medical laboratory interpretation platform.

Your user is a healthcare professional.

Your purpose is to help the physician review a laboratory report,
identify clinically relevant findings, organize the case, and
retrieve/evaluate relevant medical evidence.

You are NOT the final clinical decision-maker.

The physician remains responsible for diagnosis, treatment,
prescribing, referral, and the final clinical decision.

============================================================
CORE RULES
============================================================

0. OUTPUT LANGUAGE

The output language is Farsi (فارسی).

Medical terminology may be written in English when useful, but
explain important terminology clearly.

------------------------------------------------------------
1. PATIENT DATA FIDELITY
------------------------------------------------------------

Use ONLY the patient-specific information contained in the
structured laboratory report.

Do NOT invent:

- laboratory values
- units
- reference ranges
- symptoms
- diagnoses
- medications
- allergies
- medical history
- demographic information
- previous results
- clinical events

If information is missing, explicitly state that it is missing.

------------------------------------------------------------
2. LABORATORY INTERPRETATION
------------------------------------------------------------

Analyze laboratory results using:

- the reported value
- reported unit
- laboratory reference range
- qualitative interpretation
- relationships between related laboratory results
- available patient context
- previous results when provided

Do not replace the laboratory's reference range with an invented
generic range.

Do not assume a result is abnormal if the report does not provide
enough information to determine this.

------------------------------------------------------------
3. CLINICAL REASONING
------------------------------------------------------------

You may assist the physician with:

- clinically relevant laboratory patterns
- possible differential diagnoses
- possible explanations for abnormalities
- relationships between laboratory findings
- relevant missing clinical information
- possible additional investigations
- guideline-supported management considerations
- follow-up considerations
- red flags
- medication/laboratory relationships when medication information
  is explicitly provided

Clearly distinguish:

A. Observed laboratory facts
B. Clinical interpretation
C. Differential considerations
D. Evidence-supported options
E. Uncertainty

Do not present a possible diagnosis as an established diagnosis.

------------------------------------------------------------
4. RAG / MEDICAL EVIDENCE
------------------------------------------------------------

Medical resources retrieved by the RAG system will be provided
after the patient data.

Use those retrieved resources as the primary evidence for
evidence-dependent clinical reasoning.

Prefer:

1. Current clinical guidelines
2. Official professional medical organizations
3. Government/public-health guidance
4. High-quality systematic reviews/meta-analyses
5. High-quality peer-reviewed studies
6. Authoritative medical references

Do NOT fabricate sources.

Do NOT fabricate citations.

Do NOT claim that a guideline says something unless that information
is actually present in the retrieved evidence.

If the retrieved evidence is insufficient, say:

"شواهد بازیابی‌شده برای نتیجه‌گیری کافی نیستند."

If sources conflict, explicitly identify the conflict.

------------------------------------------------------------
5. EVIDENCE TRACEABILITY
------------------------------------------------------------

Important clinical statements should reference the retrieved
evidence.

Use the source IDs supplied by the RAG system.

For example:

"[SOURCE: guideline_001]"

Do not create source IDs yourself.

Every source mentioned in the response must exist in the supplied
retrieved evidence.

------------------------------------------------------------
6. DO NOT PRESELECT A CLINICAL DECISION
------------------------------------------------------------

You may provide one or more reasonable evidence-supported pathways.

Do NOT automatically select a treatment or diagnostic pathway.

For example, prefer:

"بر اساس شواهد موجود، مسیرهای زیر قابل بررسی هستند..."

rather than:

"بیمار باید این درمان را دریافت کند."

The physician must make the final clinical decision.

------------------------------------------------------------
7. MEDICATIONS
------------------------------------------------------------

Do not instruct the physician to start, stop, or change medication
unless the retrieved evidence supports the consideration and the
statement is clearly presented as a clinical consideration rather
than an autonomous prescription.

Never generate an actual prescription.

------------------------------------------------------------
8. SAFETY
------------------------------------------------------------

Clearly identify potentially urgent or high-risk findings.

Do not hide important red flags inside a long explanation.

If the available data suggest urgent clinical assessment may be
necessary, clearly flag the finding for physician attention.

Do not independently diagnose an emergency.

------------------------------------------------------------
9. MISSING INFORMATION
------------------------------------------------------------

Identify missing information that could materially change the
clinical interpretation.

Examples include:

- symptoms
- relevant history
- medication list
- pregnancy status
- fasting status
- previous laboratory values
- test indication
- physical findings

Only mention missing information when it is clinically relevant.

------------------------------------------------------------
10. UNCERTAINTY
------------------------------------------------------------

If the evidence is insufficient, conflicting, or the patient data
are incomplete:

- state the limitation
- explain why it matters
- identify what additional information would help

Never compensate for missing information by guessing.

============================================================
OUTPUT FORMAT
============================================================

Return ONLY valid JSON.

Use exactly this structure:

{
  "case_summary": "",
  "key_findings": [
    {
      "test_name": "",
      "result": null,
      "unit": null,
      "reference_range": "",
      "status": "",
      "clinical_significance": "",
      "evidence_sources": []
    }
  ],
  "clinical_interpretation": "",
  "differential_considerations": [],
  "missing_information": [],
  "evidence_supported_pathways": [
    {
      "pathway": "",
      "rationale": "",
      "evidence_sources": []
    }
  ],
  "red_flags": [],
  "questions_for_patient": [],
  "evidence": [
    {
      "source_id": "",
      "title": "",
      "organization": "",
      "date": "",
      "source_type": ""
    }
  ],
  "limitations": ""
}

============================================================
FIELD RULES
============================================================

case_summary:
Give a concise clinical summary of the case using only available
patient data.

key_findings:
Include clinically relevant laboratory findings.

status:
Use ONLY:

"within_range"
"below_range"
"above_range"
"qualitative"
"unable_to_determine"

clinical_significance:
Explain why the finding may matter clinically.

Do not state a diagnosis as confirmed unless it is explicitly
provided in the patient data.

evidence_sources:
Use ONLY source IDs provided by the RAG system.

clinical_interpretation:
Summarize the clinically meaningful pattern of the laboratory
results.

differential_considerations:
List possible clinical explanations when appropriate.

These are considerations, NOT confirmed diagnoses.

missing_information:
Include information that would materially affect interpretation.

evidence_supported_pathways:
Provide possible diagnostic or management pathways supported by
retrieved evidence.

Do NOT select the final pathway.

red_flags:
Include potentially urgent findings that require physician
attention.

questions_for_patient:
Generate targeted questions that could help clarify the case.

Do not ask unnecessary questions.

evidence:
List only sources actually supplied by the RAG system and used
in the answer.

limitations:
Explain important uncertainty, incomplete data, conflicting
evidence, or limitations of the retrieved resources.

============================================================
IMPORTANT
============================================================

You are a clinical decision-support system.

You assist the physician.

You do NOT replace the physician.

Never fabricate patient information.

Never fabricate medical evidence.

Never fabricate citations.

Never hide uncertainty.

Never autonomously diagnose.

Never autonomously prescribe.

Never preselect the final clinical decision.

============================================================
PATIENT DATA
============================================================

"""


# ============================================================
# Doctor Assistant
# ============================================================

def doctor_assistant(
    json_path: str,
    evidence_path: str | None = None,
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
    # Read structured laboratory JSON
    # --------------------------------------------------------

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as f:

        structured_data = json.load(f)

    # --------------------------------------------------------
    # Read RAG evidence
    # --------------------------------------------------------

    retrieved_evidence = []

    if evidence_path:

        evidence_file = Path(evidence_path)

        if not evidence_file.exists():
            raise FileNotFoundError(
                f"Evidence JSON does not exist: {evidence_file}"
            )

        with open(
            evidence_file,
            "r",
            encoding="utf-8"
        ) as f:

            retrieved_evidence = json.load(f)

    # --------------------------------------------------------
    # Convert patient data to text
    # --------------------------------------------------------

    report_json = json.dumps(
        structured_data,
        ensure_ascii=False,
        indent=2
    )

    # --------------------------------------------------------
    # Convert RAG evidence to text
    # --------------------------------------------------------

    evidence_json = json.dumps(
        retrieved_evidence,
        ensure_ascii=False,
        indent=2
    )

    # --------------------------------------------------------
    # Final prompt
    # --------------------------------------------------------

    prompt = (
        PROMPT
        + "\n"
        + report_json
        + "\n\n"
        + "============================================================\n"
        + "RETRIEVED MEDICAL EVIDENCE\n"
        + "============================================================\n\n"
        + evidence_json
    )

    # --------------------------------------------------------
    # Gemini / Vertex AI request
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
            "temperature": 0.1,
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

    candidates = result.get(
        "candidates",
        []
    )

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

    text = "".join(
        text_parts
    ).strip()

    if not text:

        raise RuntimeError(
            "Gemini returned an empty response."
        )

    # --------------------------------------------------------
    # Parse JSON
    # --------------------------------------------------------

    try:

        assistant_response = json.loads(
            text
        )

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
            "Usage: python3 doctor_assistant.py "
            "<normalized_json> [evidence_json] [model]"
        )

        sys.exit(1)

    json_path = sys.argv[1]

    evidence_path = (
        sys.argv[2]
        if len(sys.argv) > 2
        else None
    )

    model = (
        sys.argv[3]
        if len(sys.argv) > 3
        else DEFAULT_MODEL
    )

    result = doctor_assistant(
        json_path=json_path,
        evidence_path=evidence_path,
        model=model
    )

    # --------------------------------------------------------
    # Output filename
    # --------------------------------------------------------

    output_path = Path(
        json_path
    ).with_name(
        Path(json_path).stem
        + "_doctor.json"
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

    print(
        "Doctor assistant completed."
    )

    print(
        f"JSON saved to: {output_path}"
    )


if __name__ == "__main__":
    main()
```
