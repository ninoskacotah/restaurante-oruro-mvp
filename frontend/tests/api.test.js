import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  apiRequest,
  clearToken,
  login,
  readToken,
  storeToken,
} from "../src/services/api.js";

describe("servicio de API", () => {
  beforeEach(() => {
    sessionStorage.clear();
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("conserva el token solo en sessionStorage", () => {
    storeToken("token-prueba");
    expect(readToken()).toBe("token-prueba");
    clearToken();
    expect(readToken()).toBeNull();
  });

  it("inicia sesión y guarda el token devuelto", async () => {
    fetch.mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ access_token: "jwt-seguro", token_type: "bearer" }),
    });

    await login({ nombre_usuario: "admin", contrasena: "secreta" });

    expect(readToken()).toBe("jwt-seguro");
    expect(fetch).toHaveBeenCalledWith(
      "/api/auth/login",
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("envía Bearer a las operaciones protegidas", async () => {
    storeToken("jwt-seguro");
    fetch.mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => [],
    });

    await apiRequest("/platos");

    const headers = fetch.mock.calls[0][1].headers;
    expect(headers.get("Authorization")).toBe("Bearer jwt-seguro");
  });

  it("elimina el token cuando la API devuelve 401", async () => {
    storeToken("token-vencido");
    const expiredListener = vi.fn();
    window.addEventListener("auth-expired", expiredListener, { once: true });
    fetch.mockResolvedValue({
      ok: false,
      status: 401,
      json: async () => ({ detail: "Credenciales incorrectas." }),
    });

    await expect(apiRequest("/platos")).rejects.toThrow(
      "Credenciales incorrectas.",
    );
    expect(readToken()).toBeNull();
    expect(expiredListener).toHaveBeenCalledOnce();
  });

  it("presenta un error controlado si no existe conexión", async () => {
    fetch.mockRejectedValue(new TypeError("network"));

    await expect(apiRequest("/menus")).rejects.toThrow(
      "No fue posible comunicarse con el servidor.",
    );
  });
});
