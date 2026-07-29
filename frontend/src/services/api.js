const API_ROOT = import.meta.env.VITE_API_BASE || "/api";
const TOKEN_KEY = "las-retamas-admin-token";

export function readToken() {
  return sessionStorage.getItem(TOKEN_KEY);
}

export function storeToken(token) {
  sessionStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  sessionStorage.removeItem(TOKEN_KEY);
}

export async function apiRequest(path, options = {}) {
  const headers = new Headers(options.headers || {});
  const token = readToken();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  let response;
  try {
    response = await fetch(`${API_ROOT}${path}`, { ...options, headers });
  } catch {
    throw new Error("No fue posible comunicarse con el servidor.");
  }

  if (response.status === 401) {
    clearToken();
    window.dispatchEvent(new Event("auth-expired"));
  }
  if (!response.ok) {
    let message = "La operación no pudo completarse.";
    try {
      const payload = await response.json();
      message = typeof payload.detail === "string" ? payload.detail : message;
    } catch {
      // Una respuesta no JSON conserva el mensaje seguro y general.
    }
    const error = new Error(message);
    error.status = response.status;
    throw error;
  }
  if (response.status === 204) {
    return null;
  }
  return response.json();
}

export async function login(credentials) {
  const response = await apiRequest("/auth/login", {
    method: "POST",
    body: JSON.stringify(credentials),
  });
  storeToken(response.access_token);
  return response;
}

export async function logout() {
  try {
    await apiRequest("/auth/logout", { method: "POST" });
  } finally {
    clearToken();
  }
}

export async function apiObjectUrl(path) {
  const headers = new Headers();
  const token = readToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const response = await fetch(`${API_ROOT}${path}`, { headers });
  if (response.status === 401) {
    clearToken();
    window.dispatchEvent(new Event("auth-expired"));
  }
  if (!response.ok) {
    throw new Error("No fue posible cargar el archivo protegido.");
  }
  return URL.createObjectURL(await response.blob());
}
