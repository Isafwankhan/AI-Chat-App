# AI Chat Application

A ChatGPT-style full-stack app: FastAPI + WebSocket streaming + JWT auth + Groq LLM, with a single-file terminal/pixel-themed frontend.

## Stack
- **Backend**: FastAPI, SQLAlchemy (SQLite by default, swap `DATABASE_URL` for Postgres), JWT auth (access + refresh), WebSockets
- **AI**: Groq Cloud (`llama-3.3-70b-versatile` default, model switchable per chat)
- **Frontend**: single-file HTML/JS (no build step), Tailwind-free custom CSS, `marked.js` + `highlight.js` for Markdown/code rendering

## Features implemented
- Register / Login / Refresh token / `/me`
- Chat sessions: create, list, rename, delete
- Messages persisted to DB, full history sent to LLM each turn (conversation memory)
- **Streaming responses** over WebSocket (token-by-token, like ChatGPT)
- Multiple model selection (stored per chat as `model_used`)
- **Auto-generated chat titles** via AI after first message
- Search across chat titles + message content
- Export chat as Markdown or TXT
- Markdown rendering + syntax-highlighted code blocks in the UI
- Sidebar grouped by Today / Yesterday / Last Week / Last Month / Older
- Pixel/terminal aesthetic: Press Start 2P headers, JetBrains Mono body, CRT scanline overlay, green/pink accents

## Not implemented (noted as stretch goals in the original spec)
File upload, image upload (multimodal), RAG, conversation branching, personas, voice chat, shared public links, rate limiting, usage analytics, tool calling. The backend is structured (`services/`, `api/`) so these slot in cleanly later.

## Setup

### 1. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# edit .env -> set GROQ_API_KEY (get one free at console.groq.com) and JWT_SECRET
uvicorn app.main:app --reload
```
Backend runs at `http://localhost:8000`. SQLite DB file (`chat_app.db`) is created automatically on first run.

### 2. Frontend
Just open `frontend/index.html` in a browser (it talks to `http://localhost:8000` by default — edit the `API_BASE` constant near the top of the `<script>` tag if your backend runs elsewhere). No build step needed.

### 3. Docker (backend only)
```bash
docker-compose up --build
```

## API Endpoints
| Method | Path | Description |
|---|---|---|
| POST | /register | Create account, returns tokens |
| POST | /login | Returns access + refresh tokens |
| POST | /refresh | Exchange refresh token for new pair |
| GET | /me | Current user info |
| GET | /chats | List user's chats |
| POST | /chats | Create new chat |
| PATCH | /chats/{id} | Rename chat |
| DELETE | /chats/{id} | Delete chat |
| GET | /messages/{chat_id} | Get all messages in a chat |
| GET | /search?q= | Search chats by title/content |
| POST | /export/{chat_id}?format=markdown\|txt | Export chat |
| WS | /ws/chat/{chat_id} | Streaming chat — send `{"token":...}` first, then `{"content":..., "model":...}` per message |

## WebSocket protocol
1. Client connects to `/ws/chat/{chat_id}`.
2. Client immediately sends `{"token": "<access_token>"}`.
3. For each message, client sends `{"content": "...", "model": "llama-3.3-70b-versatile"}`.
4. Server streams back:
   - `{"type":"user_message", ...}` — confirms saved user message
   - `{"type":"stream_start"}`
   - `{"type":"token","content":"..."}` — repeated per chunk
   - `{"type":"title_update","title":"..."}` — only on first message in a chat
   - `{"type":"stream_end","full_content":"..."}`

## Folder structure
```
backend/
  app/
    api/         # auth.py, chat.py, websocket.py
    services/     # llm.py (Groq), export.py
    models/       # SQLAlchemy models
    schemas/      # Pydantic schemas
    core/         # security (JWT/hashing), deps (current user)
    database/     # engine/session
    main.py
frontend/
  index.html       # entire frontend, single file
docker-compose.yml
```
