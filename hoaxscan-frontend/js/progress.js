// progress.js
// Tampilan status bertahap (stepper) dan kerangka abu-abu (skeleton) saat memuat.

// Tahapan pemeriksaan, mengikuti status dari backend:
// POST (membaca artikel) -> pending -> processing -> done / failed
export const STEPS = [
  { key: "reading", label: "Membaca artikel", note: "Mengambil judul dan isi dari link" },
  { key: "queued", label: "Masuk antrean", note: "Menunggu giliran dianalisis" },
  { key: "analyzing", label: "Menganalisis", note: "Menilai isi artikel" },
  { key: "done", label: "Hasil siap", note: "" },
];

// Status backend -> indeks tahap yang sedang berjalan.
export function stepIndexFor(status) {
  if (status === "processing") return 2;
  if (status === "done") return 3;
  return 1; // pending atau status lain yang belum dikenal
}

/**
 * active: indeks tahap yang sedang berjalan.
 * failed: true kalau tahap aktif berakhir gagal.
 */
export function renderSteps(active, { failed = false } = {}) {
  const items = STEPS.map((step, i) => {
    const state = i < active ? "done" : i === active ? (failed ? "failed" : "active") : "todo";
    const mark = state === "done" ? "✓" : state === "failed" ? "!" : i + 1;
    const stateText = { done: "selesai", active: "sedang berjalan", failed: "gagal", todo: "belum" }[state];
    return `
      <li class="step step-${state}"${state === "active" ? ' aria-current="step"' : ""}>
        <span class="step-mark" aria-hidden="true">${mark}</span>
        <span class="step-text"><b>${step.label}</b>${state === "active" && step.note ? `<small>${step.note}</small>` : ""}</span>
        <span class="visually-hidden">: ${stateText}</span>
      </li>`;
  }).join("");
  return `<ol class="steps" aria-label="Tahapan pemeriksaan">${items}</ol>`;
}

// Kerangka abu-abu untuk daftar yang sedang dimuat (Riwayat, Tren).
export function renderSkeletonList(count = 3, label = "Memuat...") {
  const rows = Array.from({ length: count }, () => `
    <div class="skeleton-row" aria-hidden="true">
      <span class="skeleton skeleton-icon"></span>
      <span class="skeleton-lines"><span class="skeleton skeleton-line"></span><span class="skeleton skeleton-line short"></span></span>
      <span class="skeleton skeleton-score"></span>
    </div>`).join("");
  return `<div class="skeleton-list" role="status"><span class="visually-hidden">${label}</span>${rows}</div>`;
}
