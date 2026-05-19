from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from app.schemas.message import (
    ContinueMessageRequest
)
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.schemas.conversation import CreateConversationRequest

from app.repositories.conversation_repo import ConversationRepository
from app.repositories.message_repo import MessageRepository
from app.repositories.user_repo import UserRepository

from app.services.chat_service import ChatService

from app.core.security import verify_password

router = APIRouter(prefix="/conversations")


@router.post("")
def create_conversation(
    request: CreateConversationRequest,
    db: Session = Depends(get_db)
):

    user = UserRepository.get_by_id(db, request.user_id)

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid user credentials")

    conversation = ConversationRepository.create(
        db,
        request.user_id,
        request.first_message[:50]
    )

    ConversationRepository.prune_conversations(db, request.user_id, keep=20)

    result = ChatService.chat(
        db,
        conversation.id,
        request.provider,
        request.first_message
    )

    return {
        "conversation_id": conversation.id,
        "response": result["content"]
    }


@router.get("")
def list_conversations(
    user_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):

    conversations = ConversationRepository.get_user_conversations(
        db,
        user_id,
        skip,
        limit
    )

    return conversations


@router.get("/{conversation_id}")
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):

    conversation = ConversationRepository.get_by_id(
        db,
        conversation_id
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    messages = MessageRepository.get_messages(
        db,
        conversation_id
    )

    return {
        "conversation_id": conversation.id,
        "messages": messages
    }


@router.put("/{conversation_id}/messages")
def continue_chat(
    conversation_id: int,
    request: ContinueMessageRequest,
    db: Session = Depends(get_db)
):

    conversation = ConversationRepository.get_by_id(
        db,
        conversation_id
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    if conversation.user_id != request.user_id:
        raise HTTPException(
            status_code=403,
            detail="User is not allowed to access this conversation"
        )

    user = UserRepository.get_by_id(db, request.user_id)

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid user credentials")

    result = ChatService.chat(
        db,
        conversation_id,
        request.provider,
        request.message
    )

    return {
        "response": result["content"]
    }


@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):

    conversation = ConversationRepository.get_by_id(
        db,
        conversation_id
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    ConversationRepository.delete(
        db,
        conversation
    )

    return {
        "message": "Conversation deleted"
    }