
from datetime import datetime

from pydantic import BaseModel
from typing import Any


class OCRResultResponse(BaseModel):
    id: int
    document_id: int
    result: dict[str, Any]
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

