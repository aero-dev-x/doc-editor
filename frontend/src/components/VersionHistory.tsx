import { useEffect, useState } from "react";
import { listVersions, VersionOut } from "../api/versions";

interface Props {
  docId: string;
  onRestore: (content: string, title: string) => void;
  onClose: () => void;
}

export default function VersionHistory({ docId, onRestore, onClose }: Props) {
  const [versions, setVersions] = useState<VersionOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [preview, setPreview] = useState<VersionOut | null>(null);

  useEffect(() => {
    listVersions(docId)
      .then(setVersions)
      .finally(() => setLoading(false));
  }, [docId]);

  function formatDate(iso: string) {
    return new Date(iso).toLocaleString();
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal modal-wide" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Version history</h3>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        {loading ? (
          <p className="loading">Loading versions…</p>
        ) : versions.length === 0 ? (
          <p className="empty-state">No saved versions yet. Versions are created automatically when you edit.</p>
        ) : (
          <div className="version-layout">
            <ul className="version-list">
              {versions.map((v) => (
                <li
                  key={v.id}
                  className={`version-item ${preview?.id === v.id ? "active" : ""}`}
                  onClick={() => setPreview(v)}
                >
                  <span className="version-date">{formatDate(v.created_at)}</span>
                  <span className="version-by">by {v.saved_by_username ?? "unknown"}</span>
                  <span className="version-title">{v.title}</span>
                </li>
              ))}
            </ul>

            {preview && (
              <div className="version-preview">
                <div className="version-preview-header">
                  <strong>{preview.title}</strong>
                  <button
                    className="btn-primary"
                    onClick={() => { onRestore(preview.content, preview.title); onClose(); }}
                  >
                    Restore this version
                  </button>
                </div>
                <div className="version-preview-content">
                  <pre>{JSON.stringify(JSON.parse(preview.content), null, 2)}</pre>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
