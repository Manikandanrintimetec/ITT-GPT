from pydantic import BaseModel


class ChatRequest(BaseModel):

    provider: str

    message: str