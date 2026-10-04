import { api } from "../api.js";
import { navigate } from "../router.js";

const ENDPOINT = "/submissions";

export function renderScan(root) {
  root.innerHTML = `
    <div class="scan-shell">
      <div class="section-head">
        <span class="section-label">periksa artikel</span>
        <h2>Masukkan link artikel.</h2>
        <p>Tempel URL artikel yang ingin diperiksa. HoaxScan akan menganalisisnya dan menampilkan hasil beserta penjelasan.</p>
      </div>

      <form id="scan-form">
        <label for="scan-url">URL artikel</label>
        <input id="scan-url" type="url" name="url" placeholder="https://nama-media.id/berita/..." required autocomplete="url" />
        <p class="scan-help">Gunakan alamat artikel lengkap yang diawali https://</p>
        <p class="form-error" id="scan-error" role="alert" aria-live="assertive"></p>
        <button type="submit" class="button button-primary button-block" id="scan-submit">Analisis artikel</button>
      </form>
    </div>
  `;

  const form = root.querySelector("#scan-form");
  const errorEl = root.querySelector("#scan-error");
  const submitBtn = root.querySelector("#scan-submit");
  const pendingUrl = sessionStorage.getItem("hoaxscan_pending_url");
  if (pendingUrl) {
    form.elements.url.value = pendingUrl;
    sessionStorage.removeItem("hoaxscan_pending_url");
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorEl.textContent = "";
    submitBtn.disabled = true;
    submitBtn.setAttribute("aria-busy", "true");
    submitBtn.textContent = "Sedang menganalisis...";

    try {
      const url = form.elements.url.value.trim();
      const result = await api.post(ENDPOINT, { url });
      sessionStorage.setItem("hoaxscan_last_result", JSON.stringify(result));
      navigate("/result");
    } catch (err) {
      errorEl.textContent = err.message;
    } finally {
      submitBtn.disabled = false;
      submitBtn.removeAttribute("aria-busy");
      submitBtn.textContent = "Analisis artikel";
    }
  });
}
