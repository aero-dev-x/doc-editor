import { DocumentOut } from "../api/documents";

interface Props {
  doc: DocumentOut;
  currentUserId: string;
  onOpen: () => void;
  onDelete?: () => void;
}

export default function DocumentCard({ doc, currentUserId, onOpen, onDelete }: Props) {
  const isOwner = doc.owner_id === currentUserId;
  const updated = new Date(doc.updated_at).toLocaleString();

  return (
    <div className="doc-card" onClick={onOpen}>
      <div className="doc-card-body">
        <h3 className="doc-card-title">{doc.title}</h3>
        <p className="doc-card-meta">
          {!isOwner && <span className="badge-shared">Shared by {doc.owner_username}</span>}
          <span className="doc-card-date">{updated}</span>
        </p>
      </div>
      {isOwner && onDelete && (
        <button
          className="doc-card-delete"
          title="Delete document"
          onClick={(e) => {
            e.stopPropagation();
            if (confirm(`Delete "${doc.title}"?`)) onDelete();
          }}
        >
          ✕
        </button>
      )}
    </div>
  );
}
