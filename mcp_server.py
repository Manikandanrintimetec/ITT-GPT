import os
import sys
from dotenv import load_dotenv

# Load the .env file explicitly using the script's absolute path
current_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_dir, ".env")
load_dotenv(dotenv_path)

from mcp.server.fastmcp import FastMCP
from app.core.database import SessionLocal, initialize_database
from app.repositories.conversation_repo import ConversationRepository
from app.repositories.message_repo import MessageRepository
from app.services.chat_service import ChatService
from app.rag.retriever import retrieve_context
from app.core.logging import logger

# Initialize database tables on startup
try:
    initialize_database()
except Exception as e:
    logger.error(f"Failed to initialize database: {str(e)}")

# Create FastMCP server
mcp = FastMCP("RAG-Chat-Server")

@mcp.tool()
def list_conversations(user_id: int = 1, skip: int = 0, limit: int = 20) -> str:
    """
    List all conversations for a specific user.
    
    Args:
        user_id: The ID of the user whose conversations should be retrieved.
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.
    """
    db = SessionLocal()
    try:
        conversations = ConversationRepository.get_user_conversations(db, user_id=user_id, skip=skip, limit=limit)
        if not conversations:
            return f"No conversations found for user {user_id}."
        
        result = []
        for conv in conversations:
            result.append(f"ID: {conv.id} | Title: {conv.title} | Created At: {conv.created_at}")
        return "\n".join(result)
    except Exception as e:
        return f"Error retrieving conversations: {str(e)}"
    finally:
        db.close()

@mcp.tool()
def create_conversation(user_id: int = 1, title: str = "New Conversation") -> str:
    """
    Create a new conversation for a user and return the conversation details.
    
    Args:
        user_id: The ID of the user creating the conversation.
        title: The title of the conversation.
    """
    db = SessionLocal()
    try:
        conv = ConversationRepository.create(db, user_id=user_id, title=title)
        return f"Conversation created successfully. ID: {conv.id} | Title: {conv.title}"
    except Exception as e:
        return f"Error creating conversation: {str(e)}"
    finally:
        db.close()

@mcp.tool()
def get_conversation_history(conversation_id: int) -> str:
    """
    Retrieve the message history for a specific conversation in chronological order.
    Args:
        conversation_id: The ID of the conversation.
    """
    db = SessionLocal()
    try:
        messages = MessageRepository.get_messages(db, conversation_id=conversation_id)
        if not messages:
            return f"No messages found for conversation {conversation_id}."
        
        result = []
        for msg in messages:
            provider_str = f" ({msg.provider})" if msg.provider else ""
            result.append(f"[{msg.role.upper()}]{provider_str}: {msg.content}")
        return "\n\n".join(result)
    except Exception as e:
        return f"Error retrieving message history: {str(e)}"
    finally:
        db.close()

@mcp.tool()
def retrieve_rag_context(conversation_id: int, query: str, k: int = 5) -> str:
    """
    Retrieve context/snippets from uploaded PDF documents relevant to the query.
    
    Args:
        conversation_id: The ID of the conversation associated with the uploaded PDFs.
        query: The search query.
        k: The number of top relevant chunks to retrieve.
    """
    try:
        context = retrieve_context(conversation_id=conversation_id, query=query, k=k)
        if not context:
            return "No relevant context found in uploaded documents."
        return context
    except Exception as e:
        return f"Error retrieving context: {str(e)}"

@mcp.tool()
def send_chat_message(conversation_id: int, message: str, provider: str = "openai") -> str:
    """
    Send a message to the chat assistant. This retrieves relevant context from uploaded
    documents, sends the prompt to the selected LLM provider, stores both messages in
    the database, and returns the response content.
    
    Args:
        conversation_id: The ID of the conversation.
        message: The message text to send to the assistant.
        provider: The LLM provider to use (options: openai, openrouter, ollama, huggingface).
    """
    db = SessionLocal()
    try:
        response = ChatService.chat(
            db=db,
            conversation_id=conversation_id,
            provider=provider,
            message=message
        )
        return response.get("content", "Error: No content returned from LLM.")
    except Exception as e:
        return f"Error sending chat message: {str(e)}"
    finally:
        db.close()

if __name__ == "__main__":
    # Run the FastMCP server using stdio transport
    mcp.run(transport="stdio")
