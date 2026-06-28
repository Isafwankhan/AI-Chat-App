import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.database.db import SessionLocal
from app.models.models import Chat, Message
from app.core.deps import get_current_user_ws
from app.services.llm import stream_completion, generate_title

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/chat/{chat_id}")
async def chat_ws(websocket: WebSocket, chat_id: str):
    await websocket.accept()
    db = SessionLocal()
    try:
        # Auth via first message: {"token": "..."}
        auth_raw = await websocket.receive_text()
        auth_data = json.loads(auth_raw)
        token = auth_data.get("token")
        user = get_current_user_ws(token, db)
        if not user:
            await websocket.send_json({"type": "error", "message": "Unauthorized"})
            await websocket.close()
            return

        chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user.id).first()
        if not chat:
            await websocket.send_json({"type": "error", "message": "Chat not found"})
            await websocket.close()
            return

        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            user_content = data.get("content", "").strip()
            model = data.get("model") or chat.model_used
            if not user_content:
                continue

            is_first_message = len(chat.messages) == 0

            # Save user message
            user_msg = Message(chat_id=chat.id, role="user", content=user_content)
            db.add(user_msg)
            db.commit()
            db.refresh(user_msg)
            await websocket.send_json({"type": "user_message", "id": user_msg.id, "content": user_content})

            # Build history
            history = [{"role": m.role, "content": m.content} for m in chat.messages]

            # Stream AI response
            full_response = ""
            await websocket.send_json({"type": "stream_start"})
            try:
                for token_piece in stream_completion(history, model=model):
                    full_response += token_piece
                    await websocket.send_json({"type": "token", "content": token_piece})
            except Exception as e:
                await websocket.send_json({"type": "error", "message": f"AI error: {str(e)}"})
                full_response = full_response or "(error generating response)"

            # Save assistant message
            assistant_msg = Message(chat_id=chat.id, role="assistant", content=full_response)
            db.add(assistant_msg)
            chat.model_used = model

            # Auto-title on first exchange
            if is_first_message:
                new_title = generate_title(user_content, model=model)
                chat.title = new_title
                await websocket.send_json({"type": "title_update", "title": new_title})

            db.commit()
            db.refresh(chat)

            await websocket.send_json({
                "type": "stream_end",
                "message_id": assistant_msg.id,
                "full_content": full_response,
            })

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
    finally:
        db.close()
