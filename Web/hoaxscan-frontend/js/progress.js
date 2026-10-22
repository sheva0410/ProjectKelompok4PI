// progress.js
// Jalur tahapan pemeriksaan, catatan proses (log), dan kerangka abu-abu saat memuat.

const escapeHtml = (value = "") => String(value).replace(/[&<>"']/g, (char) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
}[char]));

// Tahapan pemeriksaan, mengikuti status dari backend:
// POST (membaca artikel) -> pending -> processing -> done / failed
export const STEPS = [
  { key: "reading", label: "Baca artikel", note: "Membuka halaman dan mengambil isinya" },
  { key: "queued", label: "Antre", note: "Menunggu giliran dinilai" },
  { key: "analyzing", label: "Periksa isi", note: "Menilai teks, gambar, dan video" },
  { key: "done", label: "Hasil", note: "" },
];

// Status backend -> indeks tahap yang sedang berjalan.
export function stepIndexFor(status) {
  if (status === "processing") return 2;
  if (status === "done") return 3;
  return 1; // pending atau status lain yang belum dikenal
}

/**
 * Jalur 4 segmen. active: indeks tahap yang sedang berjalan.
 * failed: true kalau tahap aktif berakhir gagal.
 */
export function renderSteps(active, { failed = false } = {}) {
  const items = STEPS.map((step, i) => {
    const state = i < active ? "done" : i === active ? (failed ? "failed" : "active") : "todo";
    const sub = { done: "selesai", failed: "gagal", active: step.note, todo: "" }[state];
    return `
      <li class="track-step is-${state}"${state === "active" ? ' aria-current="step"' : ""}>
        <span class="track-bar" aria-hidden="true"></span>
        <span class="track-label"><b>${step.label}</b>${sub ? `<small>${sub}</small>` : ""}</span>
      </li>`;
  }).join("");
  return `<ol class="track" aria-label="Tahapan pemeriksaan">${items}</ol>`;
}

// --- Catatan proses ---------------------------------------------------------
// Hanya mencatat kejadian yang benar-benar terlihat oleh frontend (link dikirim,
// perubahan status dari backend), dengan jam sesungguhnya.

const LOG_KEY = "hoaxscan_proc_log";

const STATUS_TEXT = {
  pending: "Masuk antrean",
  processing: "Penilaian isi dimulai",
  done: "Hasil siap",
};

export function newLog(id = null) {
  return { id, status: null, entries: [] };
}

export function addLog(log, text, { error = false, time = Date.now() } = {}) {
  log.entries.push({ time, text, error });
  return log;
}

// Menambah baris log kalau status pemeriksaan berubah.
export function noteStatus(log, result) {
  if (log.status === result.status) return log;
  if (result.state === "failed") addLog(log, `Berhenti: ${result.explanation}`, { error: true });
  else if (STATUS_TEXT[result.status]) addLog(log, STATUS_TEXT[result.status]);
  log.status = result.status;
  return log;
}

export function saveLog(log) {
  try {
    sessionStorage.setItem(LOG_KEY, JSON.stringify(log));
  } catch {
    // Penyimpanan tidak tersedia: log hanya hilang saat pindah halaman.
  }
}

// Mengambil log milik pemeriksaan ini; kalau tidak ada, mulai log baru.
export function loadLog(result) {
  try {
    const log = JSON.parse(sessionStorage.getItem(LOG_KEY) || "null");
    if (log && log.id === result.id && Array.isArray(log.entries)) return log;
  } catch {
    // abaikan log yang rusak
  }
  const created = new Date(result.created_at).getTime();
  return addLog(newLog(result.id), "Link diterima", { time: Number.isFinite(created) ? created : Date.now() });
}

const clock = (time) => new Date(time).toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit", second: "2-digit" });

function elapsed(from) {
  const s = Math.max(0, Math.round((Date.now() - from) / 1000));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
}

export function renderLog(log, { running = true } = {}) {
  const first = log.entries[0]?.time ?? Date.now();
  const rows = log.entries.map((e) => `
      <li${e.error ? ' class="is-error"' : ""}><time>${clock(e.time)}</time><span>${escapeHtml(e.text)}</span></li>`).join("");
  return `
    <div class="proc-log">
      <div class="proc-log-head"><span>Catatan proses</span><span>${running ? "berjalan" : "berhenti"} ${elapsed(first)}</span></div>
      <ol>${rows}</ol>
    </div>`;
}

export function hostOf(url) {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return url;
  }
}

// --- Kerangka abu-abu untuk daftar yang sedang dimuat (Riwayat, Tren) -------
export function renderSkeletonList(count = 3, label = "Memuat...") {
  const rows = Array.from({ length: count }, () => `
    <div class="skeleton-row" aria-hidden="true">
      <span class="skeleton skeleton-icon"></span>
      <span class="skeleton-lines"><span class="skeleton skeleton-line"></span><span class="skeleton skeleton-line short"></span></span>
      <span class="skeleton skeleton-score"></span>
    </div>`).join("");
  return `<div class="skeleton-list" role="status"><span class="visually-hidden">${label}</span>${rows}</div>`;
}
