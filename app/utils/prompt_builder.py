MAX_CONTEXT_TOKENS = 4000


def _truncate_context(context: str, max_chars: int = 2500) -> str:
    if len(context) <= max_chars:
        return context

    truncated = context[:max_chars]
    if "\n" in truncated:
        truncated = truncated[: truncated.rfind("\n")] or truncated

    return truncated + "\n\n[Truncated additional context]"


def build_messages(history, user_message, rag_context=""):

    system_prompt = (
        "You are a helpful AI assistant with access to retrieved document context. "
        "Use the provided context to answer the user as accurately as possible. "
        "Cite source labels exactly when you reference document content. "
        "If the answer is not contained in the documents, say that you do not know instead of inventing details."
    )

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    if rag_context:
        messages.append(
            {
                "role": "system",
                "content": (
                    "The following document excerpts are relevant to the query. "
                    "Use them to answer the question and cite sources where appropriate.\n\n"
                    f"{_truncate_context(rag_context)}"
                )
            }
        )

    for msg in history[-20:]:
        messages.append(
            {
                "role": msg.role,
                "content": msg.content
            }
        )

    messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    return messages