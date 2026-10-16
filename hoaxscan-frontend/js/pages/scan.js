import { submitUrl } from "../api.js";
import { FriendlyError, errorMarkup } from "../errors.js";
import { addLog, hostOf, newLog, noteStatus, renderLog, renderSteps, saveLog } from "../progress.js";
import { navigate } from "../router.js";

const escapeHtml = (value = "") => String(value).replace(/[&<>"']/g, (char) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
}[char]));

// Validasi di browser dengan pesan sendiri, supaya sama dengan pesan backend.
function validateUrl(value) {
  if (!value) return new FriendlyError("Link-nya masih kosong.", "Tempel alamat artikel yang ingin diperiksa.");
  try {
    const url = new URL(value);
    if (!["http:", "https:"].includes(url.protocol) || !url.hostname.includes(".")) throw new Error();
  } catch {
    return new FriendlyError("Link harus diawali http:// atau https://.", "Salin alamat lengkap dari kolom alamat browser, lalu tempel lagi.");
  }
  return null;
}

export function renderScan(root) {
  root.innerHTML = `
    <div class="scan-shell">
      <div class="section-head">
        <span class="section-label">periksa artikel</span>
        <h2>Masukkan link artikel.</h2>
        <p>Tempel URL artikel yang ingin diperiksa. HoaxScan akan menganalisisnya dan menampilkan hasil beserta penjelasan.</p>
      </div>

      <form id="scan-form" novalidate>
        <label for="scan-url">URL artikel</label>
        <input id="scan-url" type="url" name="url" placeholder="https://nama-media.id/berita/..." autocomplete="url" aria-describedby="scan-help scan-error" />
        <p class="scan-help" id="scan-help">Gunakan alamat artikel lengkap yang diawali https://</p>
        <div class="scan-progress" id="scan-progress" aria-live="polite" hidden></div>
        <div class="notice-error" id="scan-error" role="alert" hidden></div>
        <button type="submit" class="button button-primary button-block" id="scan-submit">Analisis artikel</button>
      </form>
    </div>
  `;

  const form = root.querySelector("#scan-form");
  const input = form.elements.url;
  const errorEl = root.querySelector("#scan-error");
  const progressEl = root.querySelector("#scan-progress");
  const submitBtn = root.querySelector("#scan-submit");

  const pendingUrl = sessionStorage.getItem("hoaxscan_pending_url");
  if (pendingUrl) {
    input.value = pendingUrl;
    sessionStorage.removeItem("hoaxscan_pending_url");
  }

  const showError = (err) => {
    errorEl.innerHTML = errorMarkup(err, escapeHtml);
    errorEl.hidden = false;
    input.setAttribute("aria-invalid", "true");
  };
  const clearError = () => {
    errorEl.hidden = true;
    errorEl.innerHTML = "";
    input.removeAttribute("aria-invalid");
  };
  input.addEventListener("input", clearError);

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearError();
    const url = input.value.trim();
    const invalid = validateUrl(url);
    if (invalid) {
      showError(invalid);
      input.focus();
      return;
    }

    submitBtn.disabled = true;
    submitBtn.setAttribute("aria-busy", "true");
    submitBtn.textContent = "Membaca artikel...";
    const log = addLog(newLog(), `Link dikirim: ${hostOf(url)}`);
    progressEl.innerHTML = renderSteps(0) + renderLog(log);
    progressEl.hidden = false;

    try {
      const result = await submitUrl(url);
      log.id = result.id;
      addLog(log, result.title ? `Artikel terbaca: "${result.title}"` : "Artikel terbaca");
      noteStatus(log, result);
      saveLog(log);
      sessionStorage.setItem("hoaxscan_last_result", JSON.stringify(result));
      navigate("/result");
    } catch (err) {
      addLog(log, `Berhenti: ${err.message}`, { error: true });
      progressEl.innerHTML = renderSteps(0, { failed: true }) + renderLog(log, { running: false });
      showError(err);
      submitBtn.disabled = false;
      submitBtn.removeAttribute("aria-busy");
      submitBtn.textContent = "Coba lagi";
      input.focus();
    }
  });
}
