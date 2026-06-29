import client from "./client";

export interface UserOut {
  id: string;
  email: string;
  username: string;
  created_at: string;
}

export async function register(email: string, username: string, password: string) {
  const res = await client.post<{ access_token: string }>("/auth/register", { email, username, password });
  return res.data;
}

export async function login(email: string, password: string) {
  const res = await client.post<{ access_token: string }>("/auth/login", { email, password });
  return res.data;
}

export async function getMe() {
  const res = await client.get<UserOut>("/auth/me");
  return res.data;
}
