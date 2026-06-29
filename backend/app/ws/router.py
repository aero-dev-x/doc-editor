import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import AsyncSessionLocal
from app.models.models import Document, DocumentShare
from app.services.auth_service import decode_token
from app.ws.manager import manager

router = APIRouter()


async def _authorize_ws(doc_id: str, token: str) -> dict | None:
    user_id = decode_token(token)
    if not user_id:
        return None
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Document)
            .options(selectinload(Document.owner), selectinload(Document.shares))
            .where(Document.id == doc_id)
        )
        doc = result.scalar_one_or_none()
        if not doc:
            return None
        is_owner = doc.owner_id == user_id
        is_shared = any(s.shared_with_id == user_id for s in doc.shares)
        if not is_owner and not is_shared:
            return None

        permission = "edit" if is_owner else next((s.permission for s in doc.shares if s.shared_with_id == user_id), "view")
        return {"id": user_id, "username": doc.owner.username if is_owner else next((s.shared_with.username for s in doc.shares if s.shared_with_id == user_id), user_id), "permission": permission}


@router.websocket("/ws/documents/{doc_id}")
async def document_ws(doc_id: str, ws: WebSocket, token: str = ""):
    user = await _authorize_ws(doc_id, token)
    if not user:
        await ws.close(code=4001)
        return

    await manager.connect(doc_id, ws, user)
    try:
        while True:
            raw = await ws.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                continue

            if msg.get("type") == "update" and user.get("permission") == "edit":
                await manager.broadcast_update(doc_id, ws, msg.get("content", ""), msg.get("title", ""))
    except WebSocketDisconnect:
        manager.disconnect(doc_id, ws)
        await manager.broadcast_presence(doc_id)
