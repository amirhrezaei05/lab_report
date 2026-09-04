from fastapi import FastAPI

from src.models.base import Base
from src.models.database import engine

from src.models import User, Document, ProcessedFile

from src.api.routes import users
from src.api.routes import documents
from src.api.routes import preprocessing


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Lab-to-Care API",
    version="0.1.0",
)


app.include_router(users.router)
app.include_router(documents.router)
app.include_router(preprocessing.router)


@app.get("/health")
def health():
    return {"status": "ok"}
