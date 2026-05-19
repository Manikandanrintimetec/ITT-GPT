from pydantic import BaseModel

from datetime import datetime


class MessageResponse(BaseModel):

    id: int

    role: str

    content: str

    provider: str

    prompt_tokens: int

    completion_tokens: int

    created_at: datetime

    class Config:
        from_attributes = True


class ContinueMessageRequest(BaseModel):

    user_id: int

    password: str

    provider: str

    message: str


class UpdateMessageRequest(BaseModel):

    user_id: int

    conversation_id: int

    content: str