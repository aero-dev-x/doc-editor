import client from "./client";

export interface ShareOut {
  id: string;
  document_id: string;
  shared_with_id: string;
  shared_with_email: string;
  shared_with_username: string;
  permission: string;
  created_at: string;
}

export async function listShares(docId: string): Promise<ShareOut[]> {
  const res = await client.get<ShareOut[]>(`/documents/${docId}/shares`);
  return res.data;
}

export async function shareDocument(docId: string, email: string, permission = "edit"): Promise<ShareOut> {
  const res = await client.post<ShareOut>(`/documents/${docId}/shares`, { email, permission });
  return res.data;
}

export async function revokeShare(docId: string, shareId: string): Promise<void> {
  await client.delete(`/documents/${docId}/shares/${shareId}`);
}

export async function getMyPermission(docId: string): Promise<string | null> {
  const res = await client.get<{ permission: string | null }>(`/documents/${docId}/my-permission`);
  return res.data.permission;
}
