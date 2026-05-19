from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.repositories.message_repo import MessageRepository
from app.repositories.conversation_repo import ConversationRepository

from app.llm.factory import LLMFactory

from app.rag.retriever import retrieve_context

from app.utils.prompt_builder import build_messages

from app.core.logging import logger
from app.core.exceptions import ResourceNotFoundError


class ChatService:

    @staticmethod
    def chat(
        db: Session,
        conversation_id: int,
        provider: str,
        message: str
    ):

        try:

            conversation = ConversationRepository.get_by_id(
                db,
                conversation_id
            )

            if not conversation:
                logger.warning(f"Conversation {conversation_id} not found")
                raise ResourceNotFoundError("Conversation")

            if not message or len(message.strip()) == 0:
                raise ValueError("Message cannot be empty")

            history = MessageRepository.get_messages(
                db,
                conversation_id
            )
            
            try:
                rag_context = retrieve_context(
                    conversation_id,
                    message
                )
            except Exception as e:
                logger.warning(f"RAG context retrieval failed: {str(e)}")
                rag_context = ""

            messages = build_messages(
                history,
                message,
                rag_context
            )

            llm = LLMFactory.get_llm(provider)

            result = llm.generate(messages)

            if not result or "content" not in result:
                raise ValueError("Invalid LLM response")

            MessageRepository.create(
                db,
                conversation_id,
                "user",
                message,
                provider
            )
            
            MessageRepository.create(
                db,
                conversation_id,
                "assistant",
                result["content"],
                provider,
                result.get("prompt_tokens", 0),
                result.get("completion_tokens", 0)
            )
            
            MessageRepository.prune_messages(db, conversation_id, keep=20)
            
            logger.info(f"Chat message created for conversation {conversation_id}")
            return result

        except ValueError as ve:
            logger.error(f"Validation error in ChatService: {str(ve)}")
            raise HTTPException(status_code=400, detail=str(ve))
        except ResourceNotFoundError as rne:
            raise HTTPException(status_code=rne.status_code, detail=rne.detail)
        except Exception as e:

            logger.error(f"Chat error: {str(e)}")

            raise HTTPException(
                status_code=500,
                detail=f"Chat processing failed: {str(e)}"
            )