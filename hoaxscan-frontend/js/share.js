// share.js
// Ringkasan hasil pemeriksaan yang bisa disalin atau dibagikan, misalnya ke grup WhatsApp.

const LIMIT = 280;

function shorten(text, max = LIMIT) {
  const clean = String(text || "").replace(/\s+/g, " ").trim();
  return clean.length > max ? `${clean.slice(0, max - 1).trimEnd()}…` : clean;
}

export function buildSummary(result, pct) {
  const lines = ["Dicek di HoaxScan"];
  if (result.title) lines.push(`"${shorten(result.title, 140)}"`);
  lines.push(`Hasil: ${result.verdict} (keyakinan ${pct}%)`);
  if (result.explanation) lines.push(`Alasan: ${shorten(result.explanation)}`);
  if (result.url) lines.push(`Artikel: ${result.url}`);
  lines.push("", "Ini hasil otomatis, bukan putusan akhir. Cocokkan juga dengan sumber lain sebelum membagikan.");
  return lines.join("\n");
}

// Menyalin teks. Clipboard API bisa tidak tersedia (bukan HTTPS) atau ditolak
// (halaman tidak sedang difokus), jadi selalu ada cara cadangan.
export async function copyText(text) {
  if (navigator.clipboard?.writeText && window.isSecureContext) {
    try {
      await navigator.clipboard.writeText(text);
      return;
    } catch {
      // lanjut ke cara cadangan
    }
  }
  const area = document.createElement("textarea");
  area.value = text;
  area.setAttribute("readonly", "");
  area.style.position = "fixed";
  area.style.opacity = "0";
  document.body.appendChild(area);
  area.select();
  const ok = document.execCommand("copy");
  area.remove();
  if (!ok) throw new Error("Gagal menyalin");
}

export const canNativeShare = () => typeof navigator.share === "function" && window.isSecureContext;
