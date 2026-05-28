from pydantic import BaseModel


class CreateConversationRequest(BaseModel):

    user_id: int

    password: str

    first_message: str

    provider: str


class ConversationResponse(BaseModel):

    id: int

    title: str