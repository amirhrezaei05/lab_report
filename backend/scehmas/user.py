from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str


class UserResponse(BaseModel):
    id: int
    username: str

    model_config = {
        "from_attributes": True
    }