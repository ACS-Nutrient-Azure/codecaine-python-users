const API_BASE = "/api";

let _token: string | null = localStorage.getItem("access_token");
let _cognitoId: string | null = localStorage.getItem("cognito_id");

export function setToken(token: string) {
  _token = token;
  localStorage.setItem("access_token", token);
}

export function getToken() {
  return _token;
}

export function setCognitoId(id: string) {
  _cognitoId = id;
  localStorage.setItem("cognito_id", id);
}

export function getCognitoId() {
  return _cognitoId;
}

export function clearAuth() {
  _token = null;
  _cognitoId = null;
  localStorage.removeItem("access_token");
  localStorage.removeItem("cognito_id");
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

  if (res.status === 401) {
    clearAuth();
    throw new Error("401");
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `HTTP ${res.status}`);
  }

  if (res.status === 204) return null;
  const text = await res.text();
  return text ? JSON.parse(text) : null;
}

export const api = {
  // Auth (dev only)
  getDevToken: (cognitoId: string) =>
    fetch(`/dev/token/${cognitoId}`).then((r) => r.json()),

  // Profile
  getProfile: (cognitoId: string) => request(`/users/${cognitoId}`),
  updateProfile: (cognitoId: string, data: any) =>
    request(`/users/${cognitoId}`, { method: "PUT", body: JSON.stringify(data) }),

  // Supplements
  getSupplements: (cognitoId: string, isActive?: boolean) => {
    const params = new URLSearchParams({ cognito_id: cognitoId });
    if (isActive !== undefined) params.set("is_active", String(isActive));
    return request(`/supplements?${params}`);
  },
  createSupplement: (data: any) =>
    request("/supplements", { method: "POST", body: JSON.stringify(data) }),
  updateSupplement: (id: number, data: any) =>
    request(`/supplements/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  deleteSupplement: (id: number) =>
    request(`/supplements/${id}`, { method: "DELETE" }),
  toggleSupplementStatus: (id: number, isActive: boolean) =>
    request(`/supplements/${id}/status`, {
      method: "PATCH",
      body: JSON.stringify({ ans_is_active: isActive }),
    }),
};
