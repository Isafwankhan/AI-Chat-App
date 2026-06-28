from typing import List
from app.models.models import Message


def export_markdown(title: str, messages: List[Message]) -> str:
    lines = [f"# {title}", ""]
    for m in messages:
        speaker = "**You**" if m.role == "user" else "**Assistant**" if m.role == "assistant" else "**System**"
        lines.append(f"{speaker}  ")
        lines.append(m.content)
        lines.append("")
    return "\n".join(lines)


def export_txt(title: str, messages: List[Message]) -> str:
    lines = [title, "=" * len(title), ""]
    for m in messages:
        speaker = "You" if m.role == "user" else "Assistant" if m.role == "assistant" else "System"
        lines.append(f"{speaker}: {m.content}")
        lines.append("")
    return "\n".join(lines)
