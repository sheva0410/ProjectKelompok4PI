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

// Contoh link untuk dicoba (diambil dari daftar uji FE-09).
const EXAMPLES = [
  { label: "Berita video ANTARA", url: "https://www.antaranews.com/berita/5790153/kpk-amankan-20-orang-termasuk-bupati-melalui-ott-di-klaten" },
  { label: "Cek fakta Kompas", url: "https://www.kompas.com/cekfakta/read/2026/10/16/092838282/hoaks-prabowo-tunjuk-ahy-sebagai-wapres-pada-september-2026" },
  { label: "Situs yang memblokir", url: "https://nasional.tempo.co/read/2121699/satgas-prr-bikin-sumur-bor-untuk-warga-terdampak-banjir-aceh-utara" },
];

// Membaca clipboard hanya bisa di HTTPS atau localhost, dan tidak semua browser mendukungnya.
const canPaste = () => typeof navigator.clipboard?.readText === "function" && window.isSecureContext;

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
        <div class="url-row">
          <input id="scan-url" type="url" name="url" placeholder="https://nama-media.id/berita/..." autocomplete="url" aria-describedby="scan-help scan-error" />
          ${canPaste() ? '<button type="button" class="button paste-button" id="scan-paste">Tempel</button>' : ""}
        </div>
        <p class="scan-help" id="scan-help">Gunakan alamat artikel lengkap yang diawali https://</p>
        <div class="examples">
          <span class="examples-label">Belum punya link? Coba contoh:</span>
          ${EXAMPLES.map((ex) => `<button type="button" class="example-chip" data-url="${ex.url}">${ex.label}</button>`).join("")}
        </div>
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

  root.querySelectorAll(".example-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      if (submitBtn.disabled) return;
      clearError();
      input.value = chip.dataset.url;
      form.requestSubmit();
    });
  });

  root.querySelector("#scan-paste")?.addEventListener("click", async () => {
    clearError();
    try {
      const text = (await navigator.clipboard.readText()).trim();
      if (!text) {
        showError(new FriendlyError("Clipboard masih kosong.", "Salin dulu link artikelnya, lalu tekan Tempel."));
        return;
      }
      input.value = text;
      input.focus();
    } catch {
      showError(new FriendlyError("Isi clipboard tidak bisa dibaca.", "Izinkan akses clipboard, atau tempel manual dengan menekan lama kolom link."));
    }
  });

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
