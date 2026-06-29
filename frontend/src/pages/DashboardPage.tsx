import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { createDocument, deleteDocument, DocumentOut, listMyDocuments, listSharedDocuments } from "../api/documents";
import DocumentCard from "../components/DocumentCard";
import FileUploadButton from "../components/FileUploadButton";
import { useAuth } from "../contexts/AuthContext";

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [myDocs, setMyDocs] = useState<DocumentOut[]>([]);
  const [sharedDocs, setSharedDocs] = useState<DocumentOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const [mine, shared] = await Promise.all([listMyDocuments(), listSharedDocuments()]);
      setMyDocs(mine);
      setSharedDocs(shared);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function handleNew() {
    setCreating(true);
    try {
      const doc = await createDocument();
      navigate(`/documents/${doc.id}`);
    } finally {
      setCreating(false);
    }
  }

  async function handleDelete(id: string) {
    await deleteDocument(id);
    setMyDocs((prev) => prev.filter((d) => d.id !== id));
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1 className="brand">DocEditor</h1>
        <div className="dashboard-actions">
          <FileUploadButton onUploaded={(id) => navigate(`/documents/${id}`)} />
          <button className="btn-primary" onClick={handleNew} disabled={creating}>
            {creating ? "Creating…" : "+ New Document"}
          </button>
          <button className="btn-ghost" onClick={logout}>
            Sign out ({user?.username})
          </button>
        </div>
      </header>

      <main className="dashboard-content">
        {loading ? (
          <p className="loading">Loading documents…</p>
        ) : (
          <>
            <section>
              <h2 className="section-heading">My Documents</h2>
              {myDocs.length === 0 ? (
                <p className="empty-state">No documents yet. Create one above.</p>
              ) : (
                <div className="doc-grid">
                  {myDocs.map((doc) => (
                    <DocumentCard
                      key={doc.id}
                      doc={doc}
                      currentUserId={user!.id}
                      onOpen={() => navigate(`/documents/${doc.id}`)}
                      onDelete={() => handleDelete(doc.id)}
                    />
                  ))}
                </div>
              )}
            </section>

            <section>
              <h2 className="section-heading">Shared with me</h2>
              {sharedDocs.length === 0 ? (
                <p className="empty-state">No documents have been shared with you yet.</p>
              ) : (
                <div className="doc-grid">
                  {sharedDocs.map((doc) => (
                    <DocumentCard
                      key={doc.id}
                      doc={doc}
                      currentUserId={user!.id}
                      onOpen={() => navigate(`/documents/${doc.id}`)}
                    />
                  ))}
                </div>
              )}
            </section>
          </>
        )}
      </main>
    </div>
  );
}
