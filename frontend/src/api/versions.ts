import client from "./client";

export interface VersionOut {
  id: string;
  document_id: string;
  title: string;
  content: string;
  saved_by_id: string | null;
  saved_by_username: string | null;
  created_at: string;
}

export async function listVersions(docId: string): Promise<VersionOut[]> {
  const res = await client.get<VersionOut[]>(`/documents/${docId}/versions`);
  return res.data;
}

export async function getVersion(docId: string, versionId: string): Promise<VersionOut> {
  const res = await client.get<VersionOut>(`/documents/${docId}/versions/${versionId}`);
  return res.data;
}
