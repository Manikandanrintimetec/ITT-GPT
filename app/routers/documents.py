import os
import shutil

from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
from fastapi import HTTPException
from fastapi import Depends
from app.schemas.document import DocumentChatRequest
from sqlalchemy.orm import Session

from app.rag.pdf_loader import load_and_split_pdf
from app.rag.vectordb import create_vector_store
from app.services.chat_service import ChatService
from app.repositories.conversation_repo import ConversationRepository
from app.core.database import get_db

router = APIRouter(prefix="/documents")

os.makedirs("uploads", exist_ok=True)


@router.post("/upload")
def upload_document(
    user_id: int,
    conversation_id: int,
    file: UploadFile = File(...),
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

    if conversation.user_id != user_id:
        raise HTTPException(
            status_code=403,
            detail="User is not allowed to upload to this conversation"
        )

    folder = f"uploads/{conversation_id}"

    os.makedirs(folder, exist_ok=True)

    file_path = f"{folder}/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    docs = load_and_split_pdf(file_path)

    create_vector_store(
        conversation_id,
        docs
    )

    return {
        "message": "Document uploaded successfully",
        "conversation_id": conversation_id,
        "file_name": file.filename
    }


@router.post("/chat")
def chat_with_pdf(
    request: DocumentChatRequest,
    db: Session = Depends(get_db)
):
    conversation = ConversationRepository.get_by_id(
        db,
        request.conversation_id
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

    result = ChatService.chat(
        db,
        request.conversation_id,
        request.provider,
        request.message
    )

    return {
        "conversation_id": request.conversation_id,
        "response": result["content"]
    }