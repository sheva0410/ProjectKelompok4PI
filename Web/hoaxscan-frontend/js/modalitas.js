// modalitas.js
// Lencana modalitas (teks / gambar / video) untuk menunjukkan bagian artikel
// yang benar-benar dinilai oleh sistem, dipakai di halaman Hasil dan Riwayat.
// Sumber data: result.modalitas_dinilai dari backend (list of string).

const MODALITAS = [
  { key: "teks", label: "Teks", aliases: ["teks", "text"] },
  { key: "gambar", label: "Gambar", aliases: ["gambar", "image", "foto"] },
  { key: "video", label: "Video", aliases: ["video"] },
];

const escapeHtml = (value = "") => String(value).replace(/[&<>"']/g, (char) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
}[char]));

function keyOf(value) {
  const text = String(value).trim().toLowerCase();
  return MODALITAS.find((m) => m.aliases.includes(text))?.key || null;
}

// Mengubah daftar dari backend jadi { known: Set(key), other: [teks tak dikenal] }.
function parse(list) {
  const known = new Set();
  const other = [];
  for (const value of Array.isArray(list) ? list : []) {
    const key = keyOf(value);
    if (key) known.add(key);
    else if (String(value).trim()) other.push(String(value).trim());
  }
  return { known, other };
}

// Teks ringkas untuk daftar detail, misalnya "Teks, Gambar".
export function modalitasText(list) {
  const { known, other } = parse(list);
  const labels = MODALITAS.filter((m) => known.has(m.key)).map((m) => m.label);
  return [...labels, ...other].join(", ") || "Belum ada yang dinilai";
}

// Peringatan kalau artikel memuat media yang belum ikut dinilai.
// Butuh result.media_found (misalnya ["gambar", "video"]). Backend belum
// mengirim data ini, jadi selama kosong peringatan tidak ditampilkan.
function gapMarkup(result, known) {
  const found = (Array.isArray(result.media_found) ? result.media_found : []).map(keyOf).filter(Boolean);
  const missing = MODALITAS.filter((m) => found.includes(m.key) && !known.has(m.key)).map((m) => m.label.toLowerCase());
  if (!missing.length) return "";
  return `<p class="media-gap" role="note"><strong>Belum ikut diperiksa.</strong> Artikel ini juga memuat ${escapeHtml(missing.join(" dan "))} yang belum dinilai, jadi hasil di atas hanya mencerminkan bagian yang dinilai.</p>`;
}

export function renderModalitasBadges(result) {
  const { known, other } = parse(result.modalitas_dinilai);
  const badges = MODALITAS.map((m) => {
    const on = known.has(m.key);
    return `<li class="modality-badge ${on ? "on" : "off"}" aria-label="${m.label}: ${on ? "dinilai" : "belum dinilai"}"><span aria-hidden="true">${on ? "✓" : "–"}</span> ${m.label}</li>`;
  });
  for (const name of other) {
    badges.push(`<li class="modality-badge on" aria-label="${escapeHtml(name)}: dinilai"><span aria-hidden="true">✓</span> ${escapeHtml(name)}</li>`);
  }
  return `
    <div class="modality-block">
      <span class="modality-title">Bagian yang dinilai</span>
      <ul class="modality-list">${badges.join("")}</ul>
      ${gapMarkup(result, known)}
    </div>`;
}
