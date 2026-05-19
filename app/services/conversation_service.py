from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.repositories.conversation_repo import (
    ConversationRepository
)


class ConversationService:

    @staticmethod
    def get_conversation(
        db: Session,
        conversation_id: int
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

        return conversation

    @staticmethod
    def delete_conversation(
        db: Session,
        conversation_id: int
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
            "message": "Conversation deleted successfully"
        }