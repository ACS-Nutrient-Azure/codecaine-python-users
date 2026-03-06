const API_BASE = "/api/v1";

let _token: string | null = localStorage.getItem("access_token");

export function setToken(token: string) {
  _token = token;
  localStorage.setItem("access_token", token);
}

export function getToken() {
  return _token;
}

async function request(path: string, options: RequestInit = {}) {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (_token) {
    headers["Authorization"] = `Bearer ${_token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `HTTP ${res.status}`);
  }

  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  // Auth (dev only)
  getDevToken: (cognitoId: string) =>
    fetch(`/dev/token/${cognitoId}`).then((r) => r.json()),

  // Profile
  getProfile: () => request("/users/me"),
  updateProfile: (data: any) =>
    request("/users/me", { method: "PUT", body: JSON.stringify(data) }),

  // Supplements
  getSupplements: () => request("/users/me/supplements"),
  createSupplement: (data: any) =>
    request("/users/me/supplements", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  updateSupplement: (id: number, data: any) =>
    request(`/users/me/supplements/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  deleteSupplement: (id: number) =>
    request(`/users/me/supplements/${id}`, { method: "DELETE" }),
};
