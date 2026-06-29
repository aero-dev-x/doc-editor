import { useCallback, useEffect, useRef, useState } from "react";

interface Presence {
  id: string;
  username: string;
  permission: string;
}

interface SocketUpdate {
  content: string;
  title: string;
}

interface Options {
  docId: string;
  token: string | null;
  onRemoteUpdate: (update: SocketUpdate) => void;
}

export function useDocumentSocket({ docId, token, onRemoteUpdate }: Options) {
  const [peers, setPeers] = useState<Presence[]>([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!token) return;

    const apiUrl = import.meta.env.VITE_API_URL || "";
    const url = apiUrl
      ? `${apiUrl.replace(/^http/, "ws")}/ws/documents/${docId}?token=${token}`
      : `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.host}/ws/documents/${docId}?token=${token}`;
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => { setConnected(false); setPeers([]); };

    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        if (msg.type === "presence") setPeers(msg.users ?? []);
        if (msg.type === "update") onRemoteUpdate({ content: msg.content, title: msg.title });
      } catch {
        // ignore malformed messages
      }
    };

    return () => { ws.close(); };
  }, [docId, token]);

  const sendUpdate = useCallback((content: string, title: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "update", content, title }));
    }
  }, []);

  return { peers, connected, sendUpdate };
}
