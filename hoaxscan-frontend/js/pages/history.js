import { listSubmissions } from "../api.js";
import { modalitasText } from "../modalitas.js";

const escapeHtml = (value = "") => String(value).replace(/[&<>"']/g, (char) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
}[char]));

function formatDate(value) {
  if (!value) return "Tanggal tidak tersedia";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? escapeHtml(value) : escapeHtml(date.toLocaleString("id-ID", { dateStyle: "long", timeStyle: "short" }));
}

function safeUrl(value) {
  try {
    const url = new URL(value);
    return ["http:", "https:"].includes(url.protocol) ? url.href : "";
  } catch { return ""; }
}

function detailValue(value) {
  if (value == null || value === "") return "—";
  if (typeof value === "object") return JSON.stringify(value, null, 2);
  return String(value);
}

function formatScore(value) {
  if (value == null || value === "") return "—";
  const score = Number(value);
  if (!Number.isFinite(score)) return String(value);
  return `${Math.round(score > 0 && score <= 1 ? score * 100 : score)}%`;
}

function renderDetails(item) {
  const references = item.references || item.sources || item.sources_used || item.fact_check_sources || [];
  const refs = Array.isArray(references) ? references : [];
  const known = new Set(["id", "title", "url", "media_type", "type", "is_hoax", "verdict", "label", "confidence_score", "score", "explanation", "created_at", "state", "modalitas_dinilai", "media_found", "references", "sources", "sources_used", "fact_check_sources"]);
  const verdict = item.verdict || item.label || (item.is_hoax === true ? "Terindikasi hoax" : item.is_hoax === false ? "Cenderung kredibel" : "Tidak diketahui");
  const score = item.confidence_score ?? item.score;
  const url = safeUrl(item.url || "");
  const details = [["Status", verdict], ["Skor keyakinan", score == null ? "Tidak tersedia" : formatScore(score)], ["Jenis media", item.media_type || item.type || "Tidak tersedia"], ["Waktu pemeriksaan", formatDate(item.created_at)]];
  if (item.id != null) details.unshift(["ID pemeriksaan", item.id]);
  if (item.title) details.push(["Judul", item.title]);
  if (item.state === "done") details.push(["Modalitas dinilai", modalitasText(item.modalitas_dinilai)]);
  if (item.explanation) details.push(["Penjelasan", item.explanation]);
  for (const [key, value] of Object.entries(item)) if (!known.has(key) && value != null && value !== "") details.push([key.replaceAll("_", " "), detailValue(value)]);

  const referenceMarkup = refs.length ? `<div class="history-detail-row"><dt>Rujukan</dt><dd><ul>${refs.map((ref) => {
    const title = typeof ref === "string" ? ref : (ref.title || ref.name || ref.url || ref.link || "Rujukan");
    const refUrl = safeUrl(typeof ref === "string" ? ref : (ref.url || ref.link || ""));
    return `<li>${refUrl ? `<a href="${escapeHtml(refUrl)}" target="_blank" rel="noopener noreferrer">${escapeHtml(title)}</a>` : escapeHtml(title)}</li>`;
  }).join("")}</ul></dd></div>` : "";
  return `<div class="history-details"><dl>${details.map(([label, value]) => `<div class="history-detail-row"><dt>${escapeHtml(label)}</dt><dd>${label === "Waktu pemeriksaan" ? value : escapeHtml(value)}</dd></div>`).join("")}${url ? `<div class="history-detail-row"><dt>URL artikel</dt><dd><a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(item.url)}</a></dd></div>` : item.url ? `<div class="history-detail-row"><dt>URL artikel</dt><dd>${escapeHtml(item.url)}</dd></div>` : ""}${referenceMarkup}</dl></div>`;
}

function historyVerdict(item) {
  const status = item.verdict || item.label || "";
  if (/tidak pasti|uncertain|tidak diketahui|belum|gagal/i.test(status) || (!status && item.is_hoax == null)) return "uncertain";
  return item.is_hoax === true || (/hoax|palsu/i.test(status) && !/bukan|tidak/i.test(status)) ? "hoax" : "valid";
}

export function renderHistory(root) {
  root.innerHTML = `
    <div class="section-head"><span class="section-label">arsip pemeriksaan</span><h2>Riwayat link kamu.</h2><p>Hasil pemeriksaan yang sudah kamu lakukan.</p></div>
    <div class="history-controls" id="history-controls" hidden>
      <label for="history-search">Cari judul atau domain</label>
      <input id="history-search" type="search" placeholder="Contoh: kompas.com" autocomplete="off">
      <label for="history-filter">Hasil</label>
      <select id="history-filter"><option value="all">Semua hasil</option><option value="hoax">Terindikasi hoax</option><option value="valid">Cenderung kredibel</option><option value="uncertain">Tidak pasti / belum dianalisis</option></select>
      <p id="history-count" class="history-count" aria-live="polite"></p>
    </div>
    <div id="history-list" aria-live="polite" aria-busy="true"><div class="card" role="status">Memuat riwayat...</div></div>
  `;
  loadHistory(root);
}

function renderHistoryItems(root, items) {
  const listEl = root.querySelector("#history-list");
  const query = root.querySelector("#history-search").value.trim().toLocaleLowerCase("id-ID");
  const verdictFilter = root.querySelector("#history-filter").value;
  const filtered = items.filter((item) => {
    const text = `${item.title || ""} ${item.url || ""}`.toLocaleLowerCase("id-ID");
    return (!query || text.includes(query)) && (verdictFilter === "all" || historyVerdict(item) === verdictFilter);
  });
  root.querySelector("#history-count").textContent = `Menampilkan ${filtered.length} dari ${items.length} pemeriksaan`;
  if (!filtered.length) {
    listEl.innerHTML = `<div class="card history-no-results"><p>Tidak ada pemeriksaan yang cocok dengan pencarian dan filter ini.</p><button class="button" id="history-clear" type="button">Hapus filter</button></div>`;
    root.querySelector("#history-clear").addEventListener("click", () => {
      root.querySelector("#history-search").value = "";
      root.querySelector("#history-filter").value = "all";
      renderHistoryItems(root, items);
      root.querySelector("#history-search").focus();
    });
    listEl.setAttribute("aria-busy", "false");
    return;
  }
  listEl.innerHTML = `<div class="history-grid">${filtered.map((item, index) => `
    <article class="history-item ${historyVerdict(item)}">
      <button class="history-toggle" type="button" aria-expanded="false" aria-controls="history-detail-${index}">
        <span class="history-icon" aria-hidden="true">${escapeHtml((item.media_type || "URL").toUpperCase())}</span>
        <span class="history-body"><span class="history-type">${escapeHtml(item.title || item.url || "Pemeriksaan artikel")}</span><span class="history-date">${formatDate(item.created_at)}</span></span>
        <span class="history-score">${escapeHtml(formatScore(item.confidence_score ?? item.score))}</span><span class="history-expand" aria-hidden="true">＋</span>
      </button><div id="history-detail-${index}" class="history-detail-slot" hidden>${renderDetails(item)}</div>
    </article>`).join("")}</div>`;
  listEl.setAttribute("aria-busy", "false");
  listEl.querySelectorAll(".history-toggle").forEach((button) => button.addEventListener("click", () => {
    const expanded = button.getAttribute("aria-expanded") === "true";
    button.setAttribute("aria-expanded", String(!expanded));
    button.querySelector(".history-expand").textContent = expanded ? "＋" : "−";
    button.closest(".history-item").querySelector(".history-detail-slot").hidden = expanded;
  }));
}

async function loadHistory(root) {
  const listEl = root.querySelector("#history-list");
  try {
    const items = await listSubmissions();
    if (!items.length) {
      listEl.innerHTML = `<div class="card">Belum ada riwayat. <a href="#/scan"><strong>Periksa link pertama</strong></a></div>`;
      listEl.setAttribute("aria-busy", "false");
      return;
    }
    root.querySelector("#history-controls").hidden = false;
    root.querySelector("#history-search").addEventListener("input", () => renderHistoryItems(root, items));
    root.querySelector("#history-filter").addEventListener("change", () => renderHistoryItems(root, items));
    renderHistoryItems(root, items);
  } catch (err) {
    listEl.innerHTML = `<div class="card state-card"><p class="form-error" role="alert">Riwayat gagal dimuat: ${escapeHtml(err.message)}</p><button class="button button-primary" id="history-retry" type="button">Coba lagi</button></div>`;
    listEl.setAttribute("aria-busy", "false");
    listEl.querySelector("#history-retry").addEventListener("click", () => {
      listEl.setAttribute("aria-busy", "true");
      listEl.innerHTML = `<div class="card" role="status">Memuat riwayat...</div>`;
      loadHistory(root);
    });
  }
}
