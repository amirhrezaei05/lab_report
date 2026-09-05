from typing import Any, Optional

from pydantic import BaseModel


class PatientAssistantResult(BaseModel):
    test_name: str
    result: Any = None
    unit: Optional[str] = None
    reference_range: str = ""
    status: str
    explanation: str
    is_clinically_poblematic: bool = False


class PatientAssistantResponse(BaseModel):
    summary: str

    results: list[PatientAssistantResult]

    important_points: list[str]

    questions_for_doctor: list[str]

    safety_note: str

    dietry_paln: str = ""

    pyhsical_exccersice_plan: str = ""