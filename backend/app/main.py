from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.db import Base, engine
from app.models import models  # noqa: F401 ensures models are registered
from app.api import auth, chat, websocket

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Chat Application", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(websocket.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "AI Chat Application API"}
