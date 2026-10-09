// api.js
// Semua komunikasi ke backend HoaxScan (FastAPI) HARUS lewat file ini.
// Halaman (pages/*.js) tidak memanggil fetch() langsung; mereka memakai
// submitUrl / getSubmission / listSubmissions di bawah dan menerima bentuk
// data yang sama, baik MOCK_MODE true maupun false.

import { API_BASE_URL, MOCK_MODE } from "./config.js";
import { delay, mockAnalyzeLink, mockSaveHistory, mockGetHistory } from "./mock.js";

// Label dari backend (analysis_results.label) -> tampilan di UI.
const LABELS = {
  hoax: { is_hoax: true, verdict: "Terindikasi hoax" },
  fakta: { is_hoax: false, verdict: "Cenderung kredibel" },
  tidak_pasti: { is_hoax: null, verdict: "Tidak pasti" },
};

/**
 * Mengubah SubmissionOut dari backend menjadi bentuk yang dipakai halaman:
 * { id, url, title, media_type, state, status, is_hoax, verdict,
 *   confidence_score, explanation, references, modalitas_dinilai,
 *   created_at, error_message }
 * state: "done" (ada hasil) | "pending" (belum dianalisis) | "failed"
 */
export function toUiResult(sub) {
  const base = {
    id: sub.id,
    url: sub.url,
    title: sub.title || null,
    media_type: "link",
    status: sub.status,
    error_message: sub.error_message || null,
    created_at: sub.result?.created_at || sub.created_at,
  };

  if (sub.result) {
    const label = LABELS[sub.result.label] || LABELS.tidak_pasti;
    return {
      ...base,
      state: "done",
      is_hoax: label.is_hoax,
      verdict: label.verdict,
      confidence_score: sub.result.confidence,
      explanation: sub.result.explanation,
      references: Array.isArray(sub.result.sources) ? sub.result.sources : [],
      modalitas_dinilai: Array.isArray(sub.result.modalitas_dinilai) ? sub.result.modalitas_dinilai : [],
    };
  }

  const failed = Boolean(sub.error_message) || /fail|error|gagal/i.test(sub.status || "");
  return {
    ...base,
    state: failed ? "failed" : "pending",
    is_hoax: null,
    verdict: failed ? "Gagal diperiksa" : "Belum dianalisis",
    confidence_score: null,
    explanation: failed
      ? sub.error_message || "Artikel tidak dapat diperiksa."
      : "Link sudah diterima dan sedang menunggu analisis.",
    references: [],
  };
}

// FastAPI mengirim error validasi sebagai { detail: [{ msg, ... }] }
// dan error biasa sebagai { detail: "teks" }.
function errorMessage(data) {
  const detail = data && (data.detail ?? data.message);
  if (Array.isArray(detail)) {
    return detail.map((d) => String(d.msg || "").replace(/^Value error,\s*/i, "")).filter(Boolean).join(" ")
      || "Data yang dikirim tidak valid.";
  }
  return typeof detail === "string" && detail ? detail : "Terjadi kesalahan pada server.";
}

async function request(path, { method = "GET", body = null } = {}) {
  const config = { method, headers: { "Content-Type": "application/json" } };
  if (body !== null) config.body = JSON.stringify(body);

  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, config);
  } catch {
    throw new Error("Tidak dapat terhubung ke server. Pastikan backend sudah berjalan.");
  }

  const contentType = response.headers.get("content-type") || "";
  const data = contentType.includes("application/json") ? await response.json() : null;
  if (!response.ok) throw new Error(errorMessage(data));
  return data;
}

// POST /api/submissions -> kirim link, balikan satu pemeriksaan.
export async function submitUrl(url) {
  if (MOCK_MODE) {
    await delay(1100);
    const result = { ...mockAnalyzeLink(url), url };
    return mockSaveHistory(result);
  }
  return toUiResult(await request("/submissions", { method: "POST", body: { url } }));
}

// GET /api/submissions/{id} -> ambil ulang satu pemeriksaan (untuk cek status).
export async function getSubmission(id) {
  if (MOCK_MODE) {
    await delay(300);
    const found = mockGetHistory().find((item) => item.id === id);
    if (!found) throw new Error("Pemeriksaan tidak ditemukan.");
    return found;
  }
  return toUiResult(await request(`/submissions/${encodeURIComponent(id)}`));
}

// GET /api/submissions -> riwayat pemeriksaan, terbaru di atas.
export async function listSubmissions(limit = 100) {
  if (MOCK_MODE) {
    await delay(500);
    return mockGetHistory();
  }
  const items = await request(`/submissions?limit=${limit}`);
  return items.map(toUiResult);
}
