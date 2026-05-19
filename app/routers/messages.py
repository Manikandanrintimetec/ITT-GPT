from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.message_repo import MessageRepository
from app.repositories.conversation_repo import ConversationRepository
from app.schemas.message import UpdateMessageRequest
from app.llm.factory import LLMFactory
from app.rag.retriever import retrieve_context
from app.utils.prompt_builder import build_messages

router = APIRouter(
    prefix="/messages",
    tags=["Messages"]
)


@router.put("/{message_id}")
def update_message(
    message_id: int,
    request: UpdateMessageRequest,
    db: Session = Depends(get_db)
):
    message = MessageRepository.get_by_id(db, message_id)

    if not message:
        raise HTTPException(
            status_code=404,
            detail="Message not found"
        )

    conversation = ConversationRepository.get_by_id(
        db,
        request.conversation_id
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    if message.conversation_id != request.conversation_id:
        raise HTTPException(
            status_code=403,
            detail="Message does not belong to this conversation"
        )

    if conversation.user_id != request.user_id:
        raise HTTPException(
            status_code=403,
            detail="User is not allowed to edit messages in this conversation"
        )

    updated_message = MessageRepository.update(
        db,
        message,
        content=request.content
    )

    response_data = {
        "id": updated_message.id,
        "conversation_id": updated_message.conversation_id,
        "role": updated_message.role,
        "content": updated_message.content,
        "provider": updated_message.provider,
        "prompt_tokens": updated_message.prompt_tokens,
        "completion_tokens": updated_message.completion_tokens,
        "total_tokens": updated_message.total_tokens,
        "model_name": updated_message.model_name,
        "created_at": updated_message.created_at
    }

    if updated_message.role == "user":
        next_assistant = MessageRepository.get_next_message(
            db,
            request.conversation_id,
            updated_message.id,
            role="assistant"
        )

        if next_assistant:
            history_before = MessageRepository.get_messages_before(
                db,
                request.conversation_id,
                updated_message.id
            )

            rag_context = retrieve_context(
                request.conversation_id,
                request.content
            )

            messages = build_messages(
                history_before,
                request.content,
                rag_context
            )

            llm = LLMFactory.get_llm(updated_message.provider)
            result = llm.generate(messages)

            updated_next = MessageRepository.update(
                db,
                next_assistant,
                content=result["content"],
                prompt_tokens=result.get("prompt_tokens", next_assistant.prompt_tokens),
                completion_tokens=result.get("completion_tokens", next_assistant.completion_tokens),
                total_tokens=(
                    result.get("prompt_tokens", next_assistant.prompt_tokens)
                    + result.get("completion_tokens", next_assistant.completion_tokens)
                ),
                model_name=result.get("model_name", next_assistant.model_name)
            )

            response_data["updated_assistant_message"] = {
                "id": updated_next.id,
                "conversation_id": updated_next.conversation_id,
                "role": updated_next.role,
                "content": updated_next.content,
                "provider": updated_next.provider,
                "prompt_tokens": updated_next.prompt_tokens,
                "completion_tokens": updated_next.completion_tokens,
                "total_tokens": updated_next.total_tokens,
                "model_name": updated_next.model_name,
                "created_at": updated_next.created_at
            }

    return response_data
