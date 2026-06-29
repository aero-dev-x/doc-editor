import client from "./client";

export interface DocumentOut {
  id: string;
  title: string;
  content: string;
  owner_id: string;
  owner_email: string | null;
  owner_username: string | null;
  created_at: string;
  updated_at: string;
}

export async function listMyDocuments(): Promise<DocumentOut[]> {
  const res = await client.get<DocumentOut[]>("/documents");
  return res.data;
}

export async function listSharedDocuments(): Promise<DocumentOut[]> {
  const res = await client.get<DocumentOut[]>("/documents/shared");
  return res.data;
}

export async function createDocument(title?: string): Promise<DocumentOut> {
  const res = await client.post<DocumentOut>("/documents", { title: title || "Untitled Document" });
  return res.data;
}

export async function getDocument(id: string): Promise<DocumentOut> {
  const res = await client.get<DocumentOut>(`/documents/${id}`);
  return res.data;
}

export async function updateDocument(id: string, data: { title?: string; content?: string }): Promise<DocumentOut> {
  const res = await client.patch<DocumentOut>(`/documents/${id}`, data);
  return res.data;
}

export async function deleteDocument(id: string): Promise<void> {
  await client.delete(`/documents/${id}`);
}

export async function uploadFile(file: File): Promise<DocumentOut> {
  const form = new FormData();
  form.append("file", file);
  const res = await client.post<DocumentOut>("/documents/upload", form);
  return res.data;
}
