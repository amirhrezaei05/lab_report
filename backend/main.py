from fastapi import FastAPI


app = FastAPI()


@app.get("/")
def home():
    return {
        "message": "Patient Assistant API"
    }