"""
LLM Service for summarization and document Q&A
Uses Google AI Studio (Gemini) API; you provide the API key via environment
GEMINI_API_KEY / GOOGLE_API_KEY or in the request.
Get your key at: https://aistudio.google.com/app/apikey
"""

# ~4 chars per token; Gemini supports large context
MAX_DOC_CHARS = 120_000
MAX_CONTEXT_CHARS = 100_000

DEFAULT_MODEL = "gemini-2.5-flash"


def _truncate(text: str, max_chars: int) -> str:
    if not text or len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[... document truncated for context limit ...]"


def summarize_with_llm(document_text: str, api_key: str, model: str = None) -> str:
    """
    Summarize a document using Google AI Studio (Gemini).

    Args:
        document_text: Full document text
        api_key: Google AI Studio / Gemini API key
        model: Model name (default gemini-2.0-flash)

    Returns:
        Summary text from the LLM
    """
    try:
        from google import genai
    except ImportError:
        raise ValueError(
            "Google GenAI package required. Install with: pip install google-genai"
        )

    if not api_key or not api_key.strip():
        raise ValueError("API key is required for LLM summarization")

    client = genai.Client(api_key=api_key.strip())
    doc = _truncate(document_text, MAX_DOC_CHARS)
    model = model or DEFAULT_MODEL

    prompt = """You are a precise assistant that summarizes documents. Produce a clear, structured summary.
Include: main topic, key points, important numbers/dates, risks or obligations, and any notable exceptions or conditions.
Use short paragraphs or bullet points.

Summarize the following document:

"""
    prompt += doc

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            max_output_tokens=4096,
        ),
    )

    text = _get_response_text(response)
    return text.strip() if text else "Summary could not be generated."


def chat_with_llm(
    question: str,
    document_context: str,
    api_key: str,
    conversation_history: list = None,
    model: str = None,
) -> str:
    """
    Answer a question about the document using Google AI Studio (Gemini).

    Args:
        question: User's question
        document_context: Document text or summary to use as context
        api_key: Google AI Studio / Gemini API key
        conversation_history: Optional list of {"role": "user"|"assistant", "content": "..."}
        model: Model name

    Returns:
        LLM answer
    """
    try:
        from google import genai
    except ImportError:
        raise ValueError(
            "Google GenAI package required. Install with: pip install google-genai"
        )

    if not api_key or not api_key.strip():
        raise ValueError("API key is required for chat")

    client = genai.Client(api_key=api_key.strip())
    context = _truncate(document_context, MAX_CONTEXT_CHARS)
    model = model or DEFAULT_MODEL

    # Build prompt: system instruction + context + optional history + question
    prompt_parts = [
        "You are a helpful assistant that answers questions based ONLY on the provided document. "
        "Answer using only information from the document. If the document does not contain relevant information, say so. Be concise and accurate.",
        "",
        "Document content to use as context:",
        "---",
        context,
        "---",
    ]

    if conversation_history:
        prompt_parts.append("")
        prompt_parts.append("Previous conversation:")
        for msg in conversation_history[-10:]:
            role = "User" if msg.get("role") == "user" else "Assistant"
            prompt_parts.append(f"{role}: {msg.get('content', '')}")
        prompt_parts.append("")

    prompt_parts.append(f"User: {question}")
    prompt_parts.append("Assistant:")

    prompt = "\n".join(prompt_parts)

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            max_output_tokens=2048,
        ),
    )

    text = _get_response_text(response)
    return text.strip() if text else "I couldn't generate an answer."


def _get_response_text(response) -> str:
    """Extract text from Gemini generate_content response (handles different SDK shapes)."""
    if not response:
        return ""
    if getattr(response, "text", None):
        return response.text
    if not getattr(response, "candidates", None) or not response.candidates:
        return ""
    c = response.candidates[0]
    content = getattr(c, "content", c)
    parts = getattr(content, "parts", None) or getattr(c, "parts", None)
    if not parts:
        return ""
    return getattr(parts[0], "text", "") or ""
