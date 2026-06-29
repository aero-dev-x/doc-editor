import Underline from "@tiptap/extension-underline";
import { EditorContent, useEditor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getDocument, updateDocument } from "../api/documents";
import { getMyPermission } from "../api/shares";
import PresenceBar from "../components/PresenceBar";
import ShareModal from "../components/ShareModal";
import Toolbar from "../components/Toolbar";
import VersionHistory from "../components/VersionHistory";
import { useAuth } from "../contexts/AuthContext";
import { useAutoSave } from "../hooks/useAutoSave";
import { useDocumentSocket } from "../hooks/useDocumentSocket";

export default function EditorPage() {
  const { id } = useParams<{ id: string }>();
  const { user, token } = useAuth();
  const navigate = useNavigate();

  const [title, setTitle] = useState("Untitled Document");
  const [ownerId, setOwnerId] = useState<string | null>(null);
  const [permission, setPermission] = useState<"edit" | "view">("edit");
  const [content, setContent] = useState<string | undefined>(undefined);
  const [showShare, setShowShare] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [notFound, setNotFound] = useState(false);
  const contentInitialized = useRef(false);

  const saveStatus = useAutoSave(id, content);

  const isOwner = user?.id === ownerId;
  const canEdit = isOwner || permission === "edit";

  const handleRemoteUpdate = useCallback(({ content: remoteContent, title: remoteTitle }: { content: string; title: string }) => {
    if (editor) {
      try {
        editor.commands.setContent(JSON.parse(remoteContent));
      } catch {
        editor.commands.setContent(remoteContent);
      }
    }
    setTitle(remoteTitle);
  }, []);

  const { peers, sendUpdate } = useDocumentSocket({
    docId: id ?? "",
    token,
    onRemoteUpdate: handleRemoteUpdate,
  });

  const editor = useEditor({
    extensions: [StarterKit, Underline],
    content: "",
    editable: canEdit,
    onUpdate({ editor }) {
      const json = JSON.stringify(editor.getJSON());
      setContent(json);
      sendUpdate(json, title);
    },
  });

  useEffect(() => {
    if (editor) editor.setEditable(canEdit);
  }, [canEdit, editor]);

  useEffect(() => {
    if (!id || !user) return;

    getDocument(id)
      .then(async (doc) => {
        setTitle(doc.title);
        setOwnerId(doc.owner_id);

        if (doc.owner_id !== user.id) {
          const perm = await getMyPermission(id).catch(() => null);
          setPermission(perm === "view" ? "view" : "edit");
        } else {
          setPermission("edit");
        }

        if (editor && !contentInitialized.current) {
          contentInitialized.current = true;
          try {
            editor.commands.setContent(JSON.parse(doc.content));
          } catch {
            editor.commands.setContent(doc.content || "");
          }
          setContent(doc.content);
        }
      })
      .catch(() => setNotFound(true));
  }, [id, editor, user]);

  async function handleTitleBlur() {
    if (id && canEdit) await updateDocument(id, { title });
  }

  function handleRestore(restoredContent: string, restoredTitle: string) {
    if (editor) {
      try {
        editor.commands.setContent(JSON.parse(restoredContent));
      } catch {
        editor.commands.setContent(restoredContent);
      }
    }
    setTitle(restoredTitle);
    setContent(restoredContent);
  }

  if (notFound) {
    return (
      <div className="error-page">
        <p>Document not found or you don't have access.</p>
        <button className="btn-primary" onClick={() => navigate("/dashboard")}>Back to dashboard</button>
      </div>
    );
  }

  return (
    <div className="editor-layout">
      <div className="editor-topbar">
        <button className="btn-ghost" onClick={() => navigate("/dashboard")}>← Dashboard</button>
        <input
          className="title-input"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          onBlur={handleTitleBlur}
          placeholder="Untitled Document"
          disabled={!canEdit}
        />
        <div className="editor-meta">
          {!canEdit && <span className="badge-view-only">View only</span>}
          <span className={`save-status save-${saveStatus}`}>
            {saveStatus === "saving" && "Saving…"}
            {saveStatus === "saved" && "Saved"}
            {saveStatus === "error" && "Save failed"}
          </span>
          <button className="btn-ghost" onClick={() => setShowHistory(true)}>History</button>
          {isOwner && (
            <button className="btn-secondary" onClick={() => setShowShare(true)}>Share</button>
          )}
        </div>
      </div>

      {peers.length > 0 && user && <PresenceBar peers={peers} currentUserId={user.id} />}

      <Toolbar editor={canEdit ? editor : null} />

      <div className="editor-body">
        <EditorContent editor={editor} className={`tiptap-editor ${!canEdit ? "readonly" : ""}`} />
      </div>

      {showShare && id && <ShareModal docId={id} onClose={() => setShowShare(false)} />}
      {showHistory && id && (
        <VersionHistory docId={id} onRestore={handleRestore} onClose={() => setShowHistory(false)} />
      )}
    </div>
  );
}
