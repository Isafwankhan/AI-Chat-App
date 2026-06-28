from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.db import get_db
from app.models.models import User, Chat, Message
from app.schemas.schemas import ChatCreate, ChatOut, ChatRename, MessageOut, SearchResult
from app.core.deps import get_current_user
from app.services.export import export_markdown, export_txt

router = APIRouter(tags=["chats"])


@router.get("/chats", response_model=List[ChatOut])
def list_chats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(Chat)
        .filter(Chat.user_id == current_user.id)
        .order_by(Chat.updated_at.desc())
        .all()
    )


@router.post("/chats", response_model=ChatOut)
def create_chat(payload: ChatCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    chat = Chat(user_id=current_user.id, title=payload.title or "New Chat", model_used=payload.model_used)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


@router.patch("/chats/{chat_id}", response_model=ChatOut)
def rename_chat(chat_id: str, payload: ChatRename, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    chat.title = payload.title
    db.commit()
    db.refresh(chat)
    return chat


@router.delete("/chats/{chat_id}")
def delete_chat(chat_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    db.delete(chat)
    db.commit()
    return {"ok": True}


@router.get("/messages/{chat_id}", response_model=List[MessageOut])
def get_messages(chat_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat.messages


@router.get("/search", response_model=List[SearchResult])
def search_chats(q: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not q.strip():
        return []
    chats = db.query(Chat).filter(Chat.user_id == current_user.id).all()
    results = []
    q_lower = q.lower()
    for chat in chats:
        if q_lower in chat.title.lower():
            snippet = chat.messages[0].content[:80] if chat.messages else ""
            results.append(SearchResult(chat_id=chat.id, title=chat.title, snippet=snippet))
            continue
        for m in chat.messages:
            if q_lower in m.content.lower():
                idx = m.content.lower().find(q_lower)
                start = max(0, idx - 30)
                snippet = m.content[start:idx + 50]
                results.append(SearchResult(chat_id=chat.id, title=chat.title, snippet=snippet))
                break
    return results


@router.post("/export/{chat_id}", response_class=PlainTextResponse)
def export_chat(chat_id: str, format: str = "markdown", current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    if format == "txt":
        content = export_txt(chat.title, chat.messages)
        media_type = "text/plain"
    else:
        content = export_markdown(chat.title, chat.messages)
        media_type = "text/markdown"
    return PlainTextResponse(content=content, media_type=media_type)
