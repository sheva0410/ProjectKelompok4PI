import { getSubmission } from "../api.js";
import { renderModalitasBadges } from "../modalitas.js";
import { FriendlyError, errorMarkup } from "../errors.js";
import { addLog, loadLog, noteStatus, renderLog, renderSteps, saveLog, stepIndexFor } from "../progress.js";

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

// Cek ulang status makin jarang: 2, 2, 3, 3, lalu tiap 5 detik.
const POLL_DELAYS_MS = [2000, 2000, 3000, 3000, 5000];
const MAX_WAIT_MS = 120000;
const MAX_POLL_ERRORS = 3;

// Hanya satu timer cek ulang yang boleh aktif; dibersihkan saat pindah halaman.
let pollTimer = null;
function stopPolling() {
  clearTimeout(pollTimer);
  pollTimer = null;
}
window.addEventListener("hashchange", stopPolling);

function articleInfo(result) {
  return `
    ${result.title ? `<h2 class="result-title">${escapeHtml(result.title)}</h2>` : ""}
    ${result.url ? `<p class="scan-help">${escapeHtml(result.url)}</p>` : ""}`;
}

function drawFailed(root, result) {
  const log = noteStatus(loadLog(result), result);
  saveLog(log);
  root.innerHTML = `
    <section class="result-shell uncertain">
      <span class="section-label">pemeriksaan gagal</span>
      ${articleInfo(result)}
      ${renderSteps(2, { failed: true })}
      ${renderLog(log, { running: false })}
      <div class="notice-error" role="alert">${errorMarkup(new FriendlyError(result.explanation, result.error_hint), escapeHtml)}</div>
      <div class="result-actions">
        ${result.url ? '<button type="button" class="button button-primary" id="retry-scan">Coba periksa lagi</button>' : '<a href="#/scan" class="button button-primary">Periksa link lain</a>'}
        <a href="#/history" class="button">Lihat riwayat</a>
      </div>
    </section>
  `;
  root.querySelector("#retry-scan")?.addEventListener("click", () => {
    sessionStorage.setItem("hoaxscan_pending_url", result.url);
    window.location.hash = "#/scan";
  });
}

/**
 * poll.started: kapan mulai menunggu (ms), poll.tries: jumlah cek ulang,
 * poll.errors: galat jaringan berturut-turut, poll.lastError: galat terakhir.
 */
function drawWaiting(root, result, poll) {
  const waited = Date.now() - poll.started;
  const tooLong = waited >= MAX_WAIT_MS;
  const tooManyErrors = poll.errors >= MAX_POLL_ERRORS;
  const keepPolling = result.id != null && !tooLong && !tooManyErrors;
  const log = noteStatus(loadLog(result), result);
  saveLog(log);
  const latest = log.entries[log.entries.length - 1]?.text || result.explanation;

  let notice = "";
  if (tooManyErrors) {
    notice = `<div class="notice-error" role="alert">${errorMarkup(poll.lastError, escapeHtml)}</div>`;
  } else if (tooLong) {
    notice = `<div class="notice-warn" role="status"><strong>Analisisnya lebih lama dari biasanya.</strong><span>Prosesnya mungkin masih berjalan. Cek lagi nanti, atau buka dari halaman Riwayat.</span></div>`;
  }

  root.innerHTML = `
    <section class="result-shell uncertain">
      <span class="section-label">sedang diproses</span>
      ${articleInfo(result)}
      ${renderSteps(stepIndexFor(result.status))}
      ${renderLog(log, { running: keepPolling })}
      <p class="visually-hidden" role="status" aria-live="polite">${escapeHtml(latest)}</p>
      ${notice}
      <div class="result-actions">
        ${keepPolling ? "" : '<button type="button" class="button button-primary" id="poll-again">Cek lagi</button>'}
        <a href="#/scan" class="button${keepPolling ? " button-primary" : ""}">Periksa link lain</a>
        <a href="#/history" class="button">Lihat riwayat</a>
      </div>
    </section>
  `;

  root.querySelector("#poll-again")?.addEventListener("click", () => {
    drawWaiting(root, result, { started: Date.now(), tries: 0, errors: 0 });
  });
  if (!keepPolling) return;

  const wait = POLL_DELAYS_MS[Math.min(poll.tries, POLL_DELAYS_MS.length - 1)];
  stopPolling();
  pollTimer = setTimeout(async () => {
    if (window.location.hash !== "#/result") return;
    try {
      const fresh = await getSubmission(result.id);
      if (window.location.hash !== "#/result") return;
      sessionStorage.setItem("hoaxscan_last_result", JSON.stringify(fresh));
      drawResult(root, fresh, { ...poll, tries: poll.tries + 1, errors: 0 });
    } catch (err) {
      if (window.location.hash !== "#/result") return;
      saveLog(addLog(loadLog(result), "Status belum bisa dicek, mencoba lagi", { error: true }));
      drawWaiting(root, result, { ...poll, tries: poll.tries + 1, errors: poll.errors + 1, lastError: err });
    }
  }, wait);
}

function drawResult(root, result, poll = { started: Date.now(), tries: 0, errors: 0 }) {
  stopPolling();
  if (result.state === "failed") {
    drawFailed(root, result);
    return;
  }
  if (result.state === "pending") {
    drawWaiting(root, result, poll);
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
      ${articleInfo(result)}
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
