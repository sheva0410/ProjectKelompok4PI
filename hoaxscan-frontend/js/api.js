// api.js
// Semua komunikasi ke backend HoaxScan HARUS lewat file ini.
// Halaman (pages/*.js) tidak boleh memanggil fetch() langsung ke backend,
// supaya kalau ada perubahan, cukup diubah di sini.

import { API_BASE_URL, MOCK_MODE } from "./config.js";
import { delay, mockAnalyzeLink, mockSaveHistory, mockGetHistory } from "./mock.js";

/**
 * Fungsi inti pengirim request ke backend.
 */
async function request(path, { method = "GET", body = null } = {}) {
  const config = { method, headers: { "Content-Type": "application/json" } };
  if (body !== null) config.body = JSON.stringify(body);

  const response = await fetch(`${API_BASE_URL}${path}`, config);

  const contentType = response.headers.get("content-type") || "";
  const data = contentType.includes("application/json") ? await response.json() : null;

  if (!response.ok) {
    const message = (data && (data.detail || data.message)) || "Terjadi kesalahan pada server.";
    throw new Error(message);
  }

  return data;
}

export const api = {
  get: async (path) => {
    // --- FE-01: data contoh, tanpa backend ---
    if (MOCK_MODE && path === "/scan/history/") {
      await delay(500);
      return mockGetHistory();
    }
    return request(path);
  },

  post: async (path, body) => {
    // --- FE-01: data contoh, tanpa backend ---
    if (MOCK_MODE && path === "/submissions") {
      await delay(1100);
      const result = mockAnalyzeLink(body.url);
      result.url = body.url;
      mockSaveHistory(result);
      return result;
    }
    return request(path, { method: "POST", body });
  },
};
