import json
from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        # doc_id -> list of (websocket, user_info)
        self._connections: dict[str, list[tuple[WebSocket, dict]]] = defaultdict(list)

    async def connect(self, doc_id: str, ws: WebSocket, user: dict):
        await ws.accept()
        self._connections[doc_id].append((ws, user))
        await self._broadcast(doc_id, {"type": "presence", "users": self._user_list(doc_id)}, exclude=None)

    def disconnect(self, doc_id: str, ws: WebSocket):
        self._connections[doc_id] = [(w, u) for w, u in self._connections[doc_id] if w is not ws]
        if not self._connections[doc_id]:
            del self._connections[doc_id]

    async def broadcast_update(self, doc_id: str, sender: WebSocket, content: str, title: str):
        msg = json.dumps({"type": "update", "content": content, "title": title})
        for ws, _ in self._connections.get(doc_id, []):
            if ws is not sender:
                try:
                    await ws.send_text(msg)
                except Exception:
                    pass

    async def broadcast_presence(self, doc_id: str):
        await self._broadcast(doc_id, {"type": "presence", "users": self._user_list(doc_id)}, exclude=None)

    def _user_list(self, doc_id: str) -> list:
        return [u for _, u in self._connections.get(doc_id, [])]

    async def _broadcast(self, doc_id: str, payload: dict, exclude: WebSocket | None):
        msg = json.dumps(payload)
        for ws, _ in self._connections.get(doc_id, []):
            if ws is not exclude:
                try:
                    await ws.send_text(msg)
                except Exception:
                    pass


manager = ConnectionManager()
