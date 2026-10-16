// api.js
// Semua komunikasi ke backend HoaxScan (FastAPI) HARUS lewat file ini.
// Halaman (pages/*.js) tidak memanggil fetch() langsung; mereka memakai
// submitUrl / getSubmission / listSubmissions di bawah dan menerima bentuk
// data yang sama, baik MOCK_MODE true maupun false.
// Semua galat yang dilempar berupa FriendlyError (lihat errors.js).

import { API_BASE_URL, MOCK_MODE } from "./config.js";
import { FriendlyError, networkError, timeoutError, toFriendlyError } from "./errors.js";
import { delay, mockCreate, mockGet, mockList } from "./mock.js";

// Label dari backend (analysis_results.label) -> tampilan di UI.
const LABELS = {
  hoax: { is_hoax: true, verdict: "Terindikasi hoax" },
  fakta: { is_hoax: false, verdict: "Cenderung kredibel" },
  tidak_pasti: { is_hoax: null, verdict: "Tidak pasti" },
};

// Teks untuk submission yang belum selesai, per status backend.
const WAITING = {
  pending: { verdict: "Menunggu analisis", explanation: "Link sudah diterima dan menunggu giliran dianalisis." },
  processing: { verdict: "Sedang dianalisis", explanation: "Artikel sudah dibaca dan sedang dinilai." },
};

// Batas waktu request. POST lebih lama karena backend membaca artikel dulu.
const TIMEOUT_MS = { GET: 20000, POST: 45000 };

/**
 * Mengubah SubmissionOut dari backend menjadi bentuk yang dipakai halaman:
 * { id, url, title, media_type, state, status, is_hoax, verdict,
 *   confidence_score, explanation, error_hint, references,
 *   modalitas_dinilai, media_found, created_at, error_message }
 * state: "done" (ada hasil) | "pending" (pending/processing) | "failed"
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
  if (Array.isArray(sub.media_found)) base.media_found = sub.media_found;

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

  const failed = sub.status === "failed" || Boolean(sub.error_message) || /fail|error|gagal/i.test(sub.status || "");
  if (failed) {
    const friendly = toFriendlyError(sub.error_message || "Analisis gagal.");
    return {
      ...base,
      state: "failed",
      is_hoax: null,
      verdict: "Gagal diperiksa",
      confidence_score: null,
      explanation: friendly.message,
      error_hint: friendly.hint,
      references: [],
    };
  }

  const waiting = WAITING[sub.status] || WAITING.pending;
  return { ...base, state: "pending", is_hoax: null, confidence_score: null, references: [], ...waiting };
}

// FastAPI mengirim error validasi sebagai { detail: [{ msg, ... }] }
// dan error biasa sebagai { detail: "teks" }.
function errorDetail(data) {
  const detail = data && (data.detail ?? data.message);
  if (Array.isArray(detail)) {
    return detail.map((d) => String(d.msg || "").replace(/^Value error,\s*/i, "")).filter(Boolean).join(" ");
  }
  return typeof detail === "string" ? detail : "";
}

async function request(path, { method = "GET", body = null } = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS[method] || TIMEOUT_MS.GET);
  const config = { method, headers: { "Content-Type": "application/json" }, signal: controller.signal };
  if (body !== null) config.body = JSON.stringify(body);

  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, config);
  } catch (err) {
    throw err?.name === "AbortError" ? timeoutError() : networkError();
  } finally {
    clearTimeout(timer);
  }

  const contentType = response.headers.get("content-type") || "";
  const data = contentType.includes("application/json") ? await response.json().catch(() => null) : null;
  if (!response.ok) throw toFriendlyError(errorDetail(data), response.status);
  return data;
}

// Menjalankan versi mock dengan bentuk galat yang sama seperti backend asli.
async function fromMock(fn, wait) {
  await delay(wait);
  const out = fn();
  if (out && out.error) throw toFriendlyError(out.error.detail, out.error.status);
  return out;
}

// POST /api/submissions -> kirim link, balikan satu pemeriksaan.
export async function submitUrl(url) {
  const sub = MOCK_MODE
    ? await fromMock(() => mockCreate(url), 1500)
    : await request("/submissions", { method: "POST", body: { url } });
  return toUiResult(sub);
}

// GET /api/submissions/{id} -> ambil ulang satu pemeriksaan (untuk cek status).
export async function getSubmission(id) {
  const sub = MOCK_MODE
    ? await fromMock(() => mockGet(id), 300)
    : await request(`/submissions/${encodeURIComponent(id)}`);
  return toUiResult(sub);
}

// GET /api/submissions -> riwayat pemeriksaan, terbaru di atas.
export async function listSubmissions(limit = 100) {
  const items = MOCK_MODE
    ? await fromMock(() => mockList(), 700)
    : await request(`/submissions?limit=${limit}`);
  if (!Array.isArray(items)) throw new FriendlyError("Data riwayat dari server tidak bisa dibaca.", "Coba muat ulang halaman.");
  return items.map(toUiResult);
}
