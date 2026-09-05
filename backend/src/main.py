from fastapi import FastAPI

from src.models.base import Base
from src.models.database import engine

from src.models import User, Document, ProcessedFile

from src.api.routes import user
from src.api.routes import document
from src.api.routes import preprocessed
from src.api.routes import ocr
from src.api.routes import patient_assistant

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Lab-to-Care API",
    version="0.1.0",
)


app.include_router(user.router)
app.include_router(document.router)
app.include_router(preprocessed.router)
app.include_router(ocr.router)
app.include_router(patient_assistant.router)


@app.get("/health")
def health():
    return {"status": "ok"}
