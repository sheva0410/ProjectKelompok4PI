import { getSubmission } from "../api.js";
import { renderModalitasBadges } from "../modalitas.js";

const escapeHtml = (value = "") => String(value).replace(/[&<>"']/g, (char) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
}[char]));

function safeHttpUrl(value) {
  try {
    const url = new URL(value);
    return ["http:", "https:"].includes(url.protocol) ? url.href : null;
  } catch {
    return null;
  }
}

export function renderResult(root) {
  const raw = sessionStorage.getItem("hoaxscan_last_result");

  if (!raw) {
    root.innerHTML = `
      <div class="card" style="text-align:center;">
        <span class="section-label">belum ada pemeriksaan</span>
        <h2>Hasilnya belum tersedia.</h2>
        <p>Tempel link artikel untuk memulai pemeriksaan.</p>
        <a href="#/scan" class="button button-primary">Periksa link</a>
      </div>
    `;
    return;
  }

  let result;
  try {
    result = JSON.parse(raw);
  } catch {
    sessionStorage.removeItem("hoaxscan_last_result");
    window.location.hash = "#/scan";
    return;
  }

  drawResult(root, result);
}

const POLL_INTERVAL_MS = 3000;
const POLL_MAX_TRIES = 10;

function drawPending(root, result, tries = 0) {
  const failed = result.state === "failed";
  const waiting = !failed && result.id != null && tries < POLL_MAX_TRIES;
  root.innerHTML = `
    <section class="result-shell uncertain">
      <span class="section-label">${failed ? "pemeriksaan gagal" : "link diterima"}</span>
      <div class="result-tag">${escapeHtml(result.verdict)}</div>
      <p class="explanation">${escapeHtml(result.explanation)}</p>
      ${result.url ? `<p class="scan-help">${escapeHtml(result.url)}</p>` : ""}
      <p class="result-limit" role="status" aria-live="polite">${waiting ? "Halaman ini akan memeriksa hasilnya secara otomatis..." : failed ? "Coba periksa link lain, atau ulangi beberapa saat lagi." : "Analisis belum selesai. Kamu bisa kembali ke sini lewat Riwayat."}</p>
      <div class="result-actions">
        <a href="#/scan" class="button button-primary">Periksa link lain</a>
        <a href="#/history" class="button">Lihat riwayat</a>
      </div>
    </section>
  `;
  if (!waiting) return;

  const timer = setTimeout(async () => {
    if (!root.isConnected || !root.querySelector(".result-shell")) return;
    try {
      const fresh = await getSubmission(result.id);
      sessionStorage.setItem("hoaxscan_last_result", JSON.stringify(fresh));
      if (window.location.hash !== "#/result") return;
      drawResult(root, fresh, tries + 1);
    } catch {
      if (window.location.hash === "#/result") drawPending(root, result, tries + 1);
    }
  }, POLL_INTERVAL_MS);
  window.addEventListener("hashchange", () => clearTimeout(timer), { once: true });
}

function drawResult(root, result, tries = 0) {
  if (result.state === "pending" || result.state === "failed") {
    drawPending(root, result, tries);
    return;
  }

  const { is_hoax, confidence_score, explanation } = result;
  const rawStatus = result.verdict || result.label || "";
  const status = rawStatus || (is_hoax ? "Terindikasi hoax" : "Cenderung kredibel");
  const isUncertain = /tidak pasti|uncertain|belum/i.test(status) || (!rawStatus && is_hoax == null);
  const isHoaxResult = is_hoax ?? (/hoax|palsu/i.test(status) && !/bukan|tidak/i.test(status));
  const statusClass = isUncertain ? "uncertain" : isHoaxResult ? "hoax" : "valid";
  const score = Number(confidence_score) || 0;
  const pct = Math.max(0, Math.min(100, score > 0 && score <= 1 ? score * 100 : score));
  const references = result.references || result.sources || result.sources_used || result.fact_check_sources || [];
  const referenceItems = Array.isArray(references) ? references : [];
  const referenceMarkup = referenceItems.map((item) => {
    const title = typeof item === "string" ? item : (item.title || item.name || item.url || "Rujukan");
    const url = safeHttpUrl(typeof item === "string" ? item : (item.url || item.link || ""));
    return url
      ? `<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(title)}</a>`
      : `<p>${escapeHtml(title)}</p>`;
  }).join("");

  root.innerHTML = `
    <section class="result-shell ${statusClass}" style="--pct:${pct};">
      <span class="section-label">ringkasan pemeriksaan</span>
      ${result.title ? `<h2 class="result-title">${escapeHtml(result.title)}</h2>` : ""}
      ${result.url ? `<p class="scan-help">${escapeHtml(result.url)}</p>` : ""}
      <div class="ring" role="img" aria-label="Skor keyakinan ${pct} persen">
        <div class="ring-inner"><b>${pct}%</b><small>keyakinan</small></div>
      </div>
      <div class="result-tag">${escapeHtml(status)}</div>
      ${renderModalitasBadges(result)}
      <p class="explanation">${escapeHtml(explanation || "Belum ada penjelasan tambahan dari sistem.")}</p>
      <p class="result-limit" role="note"><strong>Gunakan sebagai petunjuk awal.</strong> Skor dan label otomatis bukan kepastian bahwa berita benar atau hoaks. Baca rujukan jika tersedia dan bandingkan dengan sumber tepercaya lain.</p>
      ${referenceMarkup ? `<div class="source-list"><h3>Rujukan terkait</h3>${referenceMarkup}</div>` : ""}
      <div class="result-actions">
        <a href="#/scan" class="button button-primary">Periksa link lain</a>
        <a href="#/history" class="button">Lihat riwayat</a>
      </div>
    </section>
  `;
}
