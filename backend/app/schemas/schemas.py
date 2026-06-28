from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict


# ---------- Auth ----------
class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    email: str
    created_at: datetime


# ---------- Chats ----------
class ChatCreate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    title: Optional[str] = "New Chat"
    model_used: Optional[str] = "llama-3.3-70b-versatile"


class ChatRename(BaseModel):
    title: str


class ChatOut(BaseModel):
    model_config = ConfigDict(protected_namespaces=(), from_attributes=True)
    id: str
    title: str
    model_used: str
    created_at: datetime
    updated_at: datetime


# ---------- Messages ----------
class MessageCreate(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    chat_id: str
    content: str
    model_used: Optional[str] = None


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    chat_id: str
    role: str
    content: str
    created_at: datetime


class SearchResult(BaseModel):
    chat_id: str
    title: str
    snippet: str
