// mock.js
// "Pura-pura backend" untuk demo tanpa server (MOCK_MODE = true di config.js).
// Bentuk datanya meniru SubmissionOut dari backend FastAPI, termasuk tahapan
// status pending -> processing -> done, supaya alur di UI sama persis.
//
// Demo galat: link yang mengandung kata kunci di MOCK_ERRORS akan gagal,
// misalnya https://contoh.id/403 atau https://contoh.id/gagal-analisis.

export const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const TRUSTED_DOMAINS = [
  "kompas.com", "detik.com", "tempo.co", "bbc.com", "reuters.com",
  "antaranews.com", "cnnindonesia.com", "katadata.co.id",
];

// Galat saat membaca artikel (dibalas langsung oleh POST, seperti 422 backend).
const MOCK_ERRORS = {
  "/403": "Situs menolak akses (HTTP 403)",
  "/404": "Situs menolak akses (HTTP 404)",
  "tidak-ada.invalid": "Domain tidak ditemukan",
  "/kosong": "Isi artikel tidak ditemukan (halaman kosong, terkunci, atau butuh login)",
};

// Lama tiap tahap (ms) sejak link dikirim.
const PENDING_MS = 2500;
const PROCESSING_MS = 6000;

// "Database" riwayat contoh, disimpan di localStorage browser.
const HISTORY_KEY = "hoaxscan_mock_history_v2";

function load() {
  try {
    return JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
  } catch {
    return [];
  }
}

function save(items) {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(items.slice(0, 20)));
}

function analyze(url) {
  const lower = (url || "").toLowerCase();
  const isTrusted = TRUSTED_DOMAINS.some((d) => lower.includes(d));
  const confidence = isTrusted ? 0.08 + Math.random() * 0.1 : 0.55 + Math.random() * 0.35;
  const isHoax = confidence >= 0.5;
  return {
    label: isHoax ? "hoax" : "fakta",
    confidence: Math.round(confidence * 100) / 100,
    explanation: isHoax
      ? "Domain sumber tidak terdaftar sebagai media terverifikasi, dan pola URL menyerupai situs yang pernah menyebarkan klaim tidak berdasar."
      : "Domain sumber terdaftar sebagai media yang umumnya melakukan verifikasi fakta sebelum publikasi.",
    sources: [],
    modalitas_dinilai: ["teks"],
  };
}

// Menghitung status submission berdasarkan waktu yang sudah berlalu.
function withStage(record) {
  const elapsed = Date.now() - new Date(record.created_at).getTime();
  const { final, fail, ...sub } = record;
  if (elapsed < PENDING_MS) return { ...sub, status: "pending", error_message: null, result: null };
  if (elapsed < PENDING_MS + PROCESSING_MS) return { ...sub, status: "processing", error_message: null, result: null };
  if (fail) return { ...sub, status: "failed", error_message: "Analisis gagal. Coba lagi nanti.", result: null };
  return {
    ...sub,
    status: "done",
    error_message: null,
    result: { ...final, created_at: new Date(new Date(record.created_at).getTime() + PENDING_MS + PROCESSING_MS).toISOString() },
  };
}

// Meniru POST /api/submissions.
export function mockCreate(url) {
  const value = String(url || "").trim();
  if (!/^https?:\/\/[^/\s]+/i.test(value)) {
    return { error: { status: 422, detail: "URL harus diawali http:// atau https://" } };
  }
  const errorKey = Object.keys(MOCK_ERRORS).find((key) => value.toLowerCase().includes(key));
  if (errorKey) return { error: { status: 422, detail: MOCK_ERRORS[errorKey] } };

  const record = {
    id: Date.now(),
    url: value,
    normalized_url: value,
    title: "Contoh judul artikel dari mode demo",
    created_at: new Date().toISOString(),
    // Meniru media yang ditemukan scraper: semua contoh punya gambar,
    // link berita video juga punya video.
    top_image: new URL("assets/og-image.png", window.location.href).href,
    video_urls: /video|20\.detik|antaranews\.com\/berita\/57901[4-9]/i.test(value) ? [value] : [],
    fail: value.toLowerCase().includes("gagal-analisis"),
    final: analyze(value),
  };
  save([record, ...load()]);
  return withStage(record);
}

// Meniru GET /api/submissions/{id}.
export function mockGet(id) {
  const record = load().find((item) => item.id === id);
  if (!record) return { error: { status: 404, detail: "Submission tidak ditemukan" } };
  return withStage(record);
}

// Meniru GET /api/submissions.
export function mockList() {
  return load().map(withStage);
}
