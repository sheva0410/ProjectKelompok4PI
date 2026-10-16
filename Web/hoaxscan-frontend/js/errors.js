// errors.js
// Mengubah galat teknis (dari backend, jaringan, atau browser) menjadi pesan
// yang mudah dipahami pengguna, lengkap dengan saran tindakan.
// Kalau backend menambah pesan galat baru, cukup tambahkan polanya di RULES.

export class FriendlyError extends Error {
  constructor(message, hint = "", { raw = "", status = 0 } = {}) {
    super(message);
    this.name = "FriendlyError";
    this.hint = hint;
    this.raw = raw;
    this.status = status;
  }
}

// Urutan penting: pola yang lebih spesifik ditaruh lebih dulu.
const RULES = [
  // Validasi URL (backend schemas.py & scraper.py)
  [/harus diawali http/i, "Link harus diawali http:// atau https://.", "Salin alamat lengkap dari kolom alamat browser, lalu tempel lagi."],
  [/terlalu panjang/i, "Link-nya terlalu panjang.", "Pastikan yang ditempel hanya satu alamat artikel."],
  [/port pada url/i, "Format link-nya tidak valid.", "Cek lagi link yang ditempel."],

  // Scraping (scraper.py)
  [/domain tidak ditemukan/i, "Alamat situsnya tidak ditemukan.", "Cek ejaan link-nya, atau pastikan situsnya masih aktif."],
  [/tidak diizinkan/i, "Link ini tidak bisa diperiksa.", "Gunakan link artikel dari situs berita yang bisa dibuka publik."],
  [/terlalu lama merespons/i, "Situs beritanya lambat merespons.", "Coba lagi beberapa saat lagi."],
  [/HTTP 404|HTTP 410/i, "Halaman artikelnya tidak ditemukan.", "Mungkin artikelnya sudah dihapus atau link-nya salah."],
  [/HTTP 40[13]/i, "Situs ini tidak mengizinkan artikelnya dibaca otomatis.", "Coba cari berita yang sama dari media lain."],
  [/HTTP 429/i, "Situs ini sedang membatasi akses.", "Tunggu sebentar, lalu coba lagi."],
  [/HTTP 5\d\d/i, "Situs beritanya sedang bermasalah.", "Coba lagi nanti, atau pakai link dari media lain."],
  [/menolak akses/i, "Situs menolak permintaan HoaxScan.", "Coba link dari media lain."],
  [/gagal mengakses url/i, "Situs beritanya tidak bisa dibuka.", "Pastikan link-nya bisa dibuka di browser, lalu coba lagi."],
  [/bukan halaman web/i, "Link ini bukan halaman artikel.", "Link ke file seperti PDF, gambar, atau video belum didukung."],
  [/halaman terlalu besar/i, "Halamannya terlalu besar untuk dibaca.", "Coba link artikel lain."],
  [/isi artikel tidak ditemukan/i, "Isi artikelnya tidak ditemukan.", "Halamannya mungkin kosong, berbayar, atau perlu login."],
  [/gagal membaca isi/i, "Isi halamannya tidak bisa dibaca.", "Coba link artikel lain."],

  // Analisis (jobs.py & analyzer.py)
  [/hasil analisis tidak valid/i, "Sistem gagal memberi penilaian yang valid.", "Coba periksa ulang link ini."],
  [/analisis gagal/i, "Analisis berhenti di tengah jalan.", "Coba periksa ulang beberapa saat lagi."],

  // Lain-lain
  [/submission tidak ditemukan|pemeriksaan tidak ditemukan/i, "Pemeriksaan ini tidak ditemukan.", "Mungkin datanya sudah dihapus. Coba periksa ulang link-nya."],
];

const GENERIC_HINT = "Coba lagi, atau periksa link lain.";

// Mengubah pesan mentah + kode HTTP menjadi FriendlyError.
export function toFriendlyError(raw, status = 0) {
  const text = String(raw || "").trim();
  for (const [pattern, message, hint] of RULES) {
    if (pattern.test(text)) return new FriendlyError(message, hint, { raw: text, status });
  }
  if (status >= 500) {
    return new FriendlyError("Server HoaxScan sedang bermasalah.", "Coba lagi beberapa saat lagi.", { raw: text, status });
  }
  if (status === 404) {
    return new FriendlyError("Data yang dicari tidak ditemukan.", GENERIC_HINT, { raw: text, status });
  }
  return new FriendlyError(text || "Terjadi kesalahan.", GENERIC_HINT, { raw: text, status });
}

export const networkError = () => new FriendlyError(
  "Server HoaxScan tidak bisa dihubungi.",
  "Cek koneksi internetmu, lalu coba lagi. Kalau masih gagal, server mungkin sedang mati.",
);

export const timeoutError = () => new FriendlyError(
  "Server terlalu lama merespons.",
  "Situs beritanya mungkin lambat dibuka. Coba lagi sebentar lagi.",
);

// Pesan galat yang dipakai bersama oleh halaman, sudah aman di-escape.
export function errorMarkup(err, escapeHtml) {
  const friendly = err instanceof FriendlyError ? err : toFriendlyError(err?.message);
  return `<strong>${escapeHtml(friendly.message)}</strong>${friendly.hint ? `<span>${escapeHtml(friendly.hint)}</span>` : ""}`;
}
