from sqlalchemy.orm import Session

from app.models.conversation import Conversation


class ConversationRepository:

    @staticmethod
    def create(
        db: Session,
        user_id: int,
        title: str
    ):

        conversation = Conversation(
            user_id=user_id,
            title=title
        )

        db.add(conversation)
        db.commit()

        db.refresh(conversation)

        return conversation

    @staticmethod
    def get_by_id(
        db: Session,
        conversation_id: int
    ):

        return db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()

    @staticmethod
    def get_user_conversations(
        db: Session,
                user_id: int,
        skip: int,
        limit: int
    ):

        return db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).offset(skip).limit(limit).all()

    @staticmethod
    def delete(
        db: Session,
        conversation
    ):

        db.delete(conversation)

        db.commit()

    @staticmethod
    def prune_conversations(db: Session, user_id: int, keep: int = 20):
        conversations_to_delete = db.query(Conversation) \
            .filter(Conversation.user_id == user_id) \
            .order_by(Conversation.created_at.desc()) \
            .offset(keep).all()

        for conversation in conversations_to_delete:
            db.delete(conversation)

        db.commit()