from fastapi import FastAPI

from src.models.base import Base
from src.models.database import engine

from src.models import User, Document, ProcessedFile

from src.api.routes import user
from src.api.routes import document
from src.api.routes import preprocessed


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Lab-to-Care API",
    version="0.1.0",
)


app.include_router(user.router)
app.include_router(document.router)
app.include_router(preprocessed.router)


@app.get("/health")
def health():
    return {"status": "ok"}
