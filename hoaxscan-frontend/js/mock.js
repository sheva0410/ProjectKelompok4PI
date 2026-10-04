// mock.js
// Semua logika "pura-pura backend" khusus untuk FE-01 (kerangka UI + data contoh).
// Dipakai oleh api.js HANYA saat MOCK_MODE true (lihat config.js).
//
// Saat FE-02 dikerjakan (sambung ke Django beneran):
//   1. Set MOCK_MODE = false di config.js
//   2. File ini tidak perlu dihapus, aman dibiarkan (tidak lagi dipanggil)

export const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const TRUSTED_DOMAINS = [
  "kompas.com", "detik.com", "tempo.co", "bbc.com", "reuters.com",
  "antaranews.com", "cnnindonesia.com", "katadata.co.id",
];

// Meniru respons pemeriksaan link saat frontend berjalan dalam mode demo.
export function mockAnalyzeLink(url) {
  const lower = (url || "").toLowerCase();
  const isTrusted = TRUSTED_DOMAINS.some((d) => lower.includes(d));
  const score = isTrusted ? 8 + Math.round(Math.random() * 10) : 55 + Math.round(Math.random() * 35);
  const is_hoax = score >= 50;

  const explanation = is_hoax
    ? "Domain sumber tidak terdaftar sebagai media terverifikasi, dan pola URL menyerupai situs yang pernah menyebarkan klaim tidak berdasar."
    : "Domain sumber terdaftar sebagai media yang umumnya melakukan verifikasi fakta sebelum publikasi.";

  return { media_type: "link", is_hoax, confidence_score: score, explanation };
}

// "Database" riwayat scan contoh, disimpan di localStorage browser.
const HISTORY_KEY = "hoaxscan_mock_history";

export function mockSaveHistory(result) {
  const history = JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
  history.unshift({ ...result, created_at: new Date().toISOString() });
  localStorage.setItem(HISTORY_KEY, JSON.stringify(history.slice(0, 20)));
}

export function mockGetHistory() {
  return JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
}
