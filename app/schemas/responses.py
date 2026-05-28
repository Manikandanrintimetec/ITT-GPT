from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class ErrorResponse(BaseModel):
    detail: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    provider: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationDetailResponse(BaseModel):
    id: int
    title: str
    user_id: int
    messages: List[MessageResponse]
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    id: int
    title: str
    user_id: int

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    conversations: List[ConversationResponse]


class ChatResponse(BaseModel):
    conversation_id: int
    response: str
    message_id: Optional[int] = None


class MessageUpdateResponse(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    updated_at: datetime
    updated_assistant_message: Optional[MessageResponse] = None

    class Config:
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    message: str
    conversation_id: int
    file_name: str


class DocumentChatResponse(BaseModel):
    conversation_id: int
    response: str


class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"
