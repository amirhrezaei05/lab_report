from datetime import datetime

from pydantic import BaseModel


class ProcessedFileResponse(BaseModel):
    id: int
    document_id: int
    file_path: str
    page_number: int | None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }