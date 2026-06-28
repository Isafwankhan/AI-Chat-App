import os
from typing import List, Dict, Generator
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

DEFAULT_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = "You are a helpful, concise AI assistant inside a ChatGPT-like app. Format responses in Markdown, and use fenced code blocks with language tags for any code."


def build_messages(history: List[Dict[str, str]], system_prompt: str = SYSTEM_PROMPT) -> List[Dict[str, str]]:
    messages = [{"role": "system", "content": system_prompt}]
    for m in history:
        messages.append({"role": m["role"], "content": m["content"]})
    return messages


def stream_completion(history: List[Dict[str, str]], model: str = DEFAULT_MODEL) -> Generator[str, None, None]:
    messages = build_messages(history)
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


def generate_title(first_message: str, model: str = DEFAULT_MODEL) -> str:
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Generate a short chat title (max 5 words, no quotes, no punctuation at the end) summarizing the user's message."},
                {"role": "user", "content": first_message},
            ],
            temperature=0.3,
            max_tokens=20,
        )
        title = resp.choices[0].message.content.strip().strip('"')
        return title[:60] if title else "New Chat"
    except Exception:
        return first_message[:40] if first_message else "New Chat"
