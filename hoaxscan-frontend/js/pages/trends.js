import { api } from "../api.js";

const escapeHtml = (value = "") => String(value).replace(/[&<>"']/g, (char) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
}[char]));

function canonicalUrl(value) {
  try {
    const url = new URL(value);
    if (!["http:", "https:"].includes(url.protocol)) return "";
    url.hash = "";
    url.search = "";
    url.pathname = url.pathname.replace(/\/+$/, "") || "/";
    return url.href;
  } catch {
    return "";
  }
}

function formatDate(value) {
  if (!value) return "Tanggal tidak tersedia";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "Tanggal tidak tersedia" : date.toLocaleDateString("id-ID", { dateStyle: "medium" });
}

export function renderTrends(root) {
  root.innerHTML = `
    <section class="trends-page">
      <header class="section-head">
        <span class="section-label">pantauan pemeriksaan</span>
        <h2>Tren link yang sering dicek.</h2>
        <p>Daftar ini dirangkum dari riwayat pemeriksaan yang tersedia untukmu. Link dengan URL artikel yang sama dikelompokkan bersama.</p>
      </header>
      <div class="trend-source-note"><strong>Cakupan data</strong><span>Urutan dan jumlah dihitung dari riwayat pemeriksaan yang dikirim aplikasi. Data agregat publik seluruh pengguna belum tersedia.</span></div>
      <div id="trends-list" aria-live="polite" aria-busy="true"><div class="card" role="status">Memuat tren...</div></div>
    </section>
  `;

  loadTrends(root.querySelector("#trends-list"));
}

async function loadTrends(listEl) {
  try {
    const history = await api.get("/scan/history/");
    const grouped = new Map();

    for (const item of history) {
      const url = canonicalUrl(item.url || "");
      if (!url) continue;
      const record = grouped.get(url) || { url, title: item.title || url, count: 0, latest: item.created_at };
      record.count += 1;
      if (!record.title || record.title === url) record.title = item.title || url;
      if (item.created_at && (!record.latest || new Date(item.created_at) > new Date(record.latest))) record.latest = item.created_at;
      grouped.set(url, record);
    }

    const trends = [...grouped.values()].sort((a, b) => b.count - a.count || new Date(b.latest || 0) - new Date(a.latest || 0)).slice(0, 10);
    if (!trends.length) {
      listEl.innerHTML = `<div class="card trend-empty"><h3>Belum ada tren untuk ditampilkan</h3><p>Setelah kamu memeriksa beberapa link, link yang berulang akan muncul di sini.</p><a class="button button-primary" href="#/scan">Periksa link</a></div>`;
      listEl.setAttribute("aria-busy", "false");
      return;
    }

    listEl.innerHTML = `<div class="trend-list">${trends.map((item, index) => `
      <article class="trend-item">
        <span class="trend-rank">${String(index + 1).padStart(2, "0")}</span>
        <div class="trend-copy">
          <h3>${escapeHtml(item.title)}</h3>
          <a class="trend-url" href="${escapeHtml(item.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(new URL(item.url).hostname + new URL(item.url).pathname)}</a>
          <span class="trend-date">Terakhir diperiksa ${escapeHtml(formatDate(item.latest))}</span>
        </div>
        <div class="trend-count"><strong>${item.count}</strong><span>kali diperiksa</span></div>
        <button class="button button-primary trend-check" type="button" data-url="${escapeHtml(item.url)}">Cek lagi</button>
      </article>
    `).join("")}</div>`;

    listEl.querySelectorAll(".trend-check").forEach((button) => {
      button.addEventListener("click", () => {
        sessionStorage.setItem("hoaxscan_pending_url", button.dataset.url);
        window.location.hash = "#/scan";
      });
    });
    listEl.setAttribute("aria-busy", "false");
  } catch (err) {
    listEl.innerHTML = `<div class="card state-card"><p class="form-error" role="alert">Tren gagal dimuat: ${escapeHtml(err.message)}</p><button class="button button-primary" id="trends-retry" type="button">Coba lagi</button></div>`;
    listEl.setAttribute("aria-busy", "false");
    listEl.querySelector("#trends-retry").addEventListener("click", () => {
      listEl.setAttribute("aria-busy", "true");
      listEl.innerHTML = `<div class="card" role="status">Memuat tren...</div>`;
      loadTrends(listEl);
    });
  }
}
