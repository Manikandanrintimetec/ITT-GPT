from pydantic import BaseModel

from datetime import datetime


class DocumentResponse(BaseModel):

    id: int

    file_name: str

    created_at: datetime

    class Config:
        from_attributes = True


class DocumentChatRequest(BaseModel):

    user_id: int

    conversation_id: int

    provider: str

    message: str