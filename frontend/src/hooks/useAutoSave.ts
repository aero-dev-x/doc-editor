import { useCallback, useEffect, useRef, useState } from "react";
import { updateDocument } from "../api/documents";

type SaveStatus = "idle" | "saving" | "saved" | "error";

export function useAutoSave(docId: string | undefined, content: string | undefined, delay = 1500) {
  const [status, setStatus] = useState<SaveStatus>("idle");
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const lastSaved = useRef<string | undefined>(undefined);

  const save = useCallback(
    async (value: string) => {
      if (!docId || value === lastSaved.current) return;
      setStatus("saving");
      try {
        await updateDocument(docId, { content: value });
        lastSaved.current = value;
        setStatus("saved");
      } catch {
        setStatus("error");
      }
    },
    [docId]
  );

  useEffect(() => {
    if (content === undefined) return;
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(() => save(content), delay);
    return () => {
      if (timer.current) clearTimeout(timer.current);
    };
  }, [content, delay, save]);

  return status;
}
