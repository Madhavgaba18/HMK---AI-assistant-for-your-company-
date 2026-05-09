from __future__ import annotations

from collections import defaultdict, deque

import ollama

from . import config, rag


SYSTEM_PROMPT = (
    "You are the AI assistant for Nova Finance, helping employees and new joinees. "
    "Answer using ONLY the context provided below. If the answer isn't in the context, "
    "say you don't have that information and suggest who they might ask. "
    "Be concise, friendly, and direct. Use bullet points for lists. "
    "Never invent names, numbers, or policies that aren't in the context."
)

GENERAL_SYSTEM_PROMPT = (
    "You are a helpful general-purpose assistant. The user's question does not "
    "appear to be about Nova Finance internal information, so answer using your "
    "general knowledge. Be concise and direct. If you are not confident about a "
    "specific fact, say so honestly rather than guessing."
)

_history: dict[str, deque[dict]] = defaultdict(
    lambda: deque(maxlen=config.HISTORY_TURNS * 2)
)


def warmup() -> None:
    ollama.chat(
        model=config.LLM_MODEL,
        messages=[{"role": "user", "content": "hi"}],
        options={"num_predict": 1},
    )


def answer(query: str, session_id: str = "default") -> str:
    chunks, max_score = rag.retrieve(query)
    use_rag = max_score >= config.RAG_THRESHOLD

    if use_rag:
        system_prompt = SYSTEM_PROMPT
        context = "\n\n---\n\n".join(chunks)
        user_message = f"Context:\n{context}\n\nQuestion: {query}"
    else:
        system_prompt = GENERAL_SYSTEM_PROMPT
        user_message = query

    history = _history[session_id]
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    response = ollama.chat(model=config.LLM_MODEL, messages=messages)
    reply = response["message"]["content"].strip()
    if not use_rag:
        reply = config.GENERAL_REPLY_PREFIX + reply

    history.append({"role": "user", "content": query})
    history.append({"role": "assistant", "content": reply})
    return reply


def reset(session_id: str = "default") -> None:
    _history.pop(session_id, None)
