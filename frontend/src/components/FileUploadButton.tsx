import { useRef, useState } from "react";
import { uploadFile } from "../api/documents";

interface Props {
  onUploaded: (docId: string) => void;
}

export default function FileUploadButton({ onUploaded }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setError("");
    setLoading(true);
    try {
      const doc = await uploadFile(file);
      onUploaded(doc.id);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Upload failed");
    } finally {
      setLoading(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <div className="upload-wrapper">
      <input ref={inputRef} type="file" accept=".txt,.md,.docx" onChange={handleChange} hidden id="file-upload" />
      <label htmlFor="file-upload" className="btn-secondary" style={{ cursor: "pointer" }}>
        {loading ? "Uploading…" : "Upload .txt / .md / .docx"}
      </label>
      {error && <p className="error">{error}</p>}
    </div>
  );
}
