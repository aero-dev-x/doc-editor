import { useEffect, useState } from "react";
import { listShares, revokeShare, shareDocument, ShareOut } from "../api/shares";

interface Props {
  docId: string;
  onClose: () => void;
}

export default function ShareModal({ docId, onClose }: Props) {
  const [shares, setShares] = useState<ShareOut[]>([]);
  const [email, setEmail] = useState("");
  const [permission, setPermission] = useState("edit");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    listShares(docId).then(setShares).catch(() => {});
  }, [docId]);

  async function handleShare(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);
    try {
      const share = await shareDocument(docId, email, permission);
      setShares((prev) => [...prev, share]);
      setEmail("");
      setSuccess(`Shared with ${share.shared_with_email}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Could not share document");
    } finally {
      setLoading(false);
    }
  }

  async function handleRevoke(share: ShareOut) {
    await revokeShare(docId, share.id);
    setShares((prev) => prev.filter((s) => s.id !== share.id));
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Share document</h3>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <form onSubmit={handleShare} className="share-form">
          <input
            type="email"
            placeholder="Colleague's email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <select value={permission} onChange={(e) => setPermission(e.target.value)}>
            <option value="edit">Can edit</option>
            <option value="view">View only</option>
          </select>
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? "Sharing…" : "Share"}
          </button>
        </form>

        {error && <p className="error">{error}</p>}
        {success && <p className="success">{success}</p>}

        {shares.length > 0 && (
          <div className="share-list">
            <h4>Shared with</h4>
            {shares.map((s) => (
              <div key={s.id} className="share-row">
                <span>{s.shared_with_email}</span>
                <span className="badge-permission">{s.permission}</span>
                <button className="btn-ghost-sm" onClick={() => handleRevoke(s)}>Remove</button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
