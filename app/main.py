from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import initialize_database
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler
)
from app.core.middleware import RateLimitMiddleware, LoggingMiddleware
from app.schemas.responses import HealthResponse

# IMPORTANT IMPORTS
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.document import Document
from app.routers.users import (
    router as user_router
)
from app.routers.conversations import router as conversation_router
from app.routers.documents import router as document_router
from app.routers.messages import router as message_router


app = FastAPI(
    title="Chat with RAG API",
    description="Multi-provider LLM chat with PDF upload and retrieval",
    version="1.0.0"
)

# Add middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=100)

# Add exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

initialize_database()


@app.get("/", response_model=HealthResponse)
def home():
    return {
        "status": "FastAPI Working",
        "version": "1.0.0"
    }


@app.get("/health", response_model=HealthResponse)
def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0"
    }


app.include_router(
    conversation_router,
    tags=["Conversations"]
)
app.include_router(
    user_router,
    tags=["Users"]
)
app.include_router(
    document_router,
    tags=["Documents"]
)
app.include_router(
    message_router,
    tags=["Messages"]
)