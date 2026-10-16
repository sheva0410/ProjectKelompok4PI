import { enableTilt } from "../tilt.js";

export function renderNotFound(root) {
  root.innerHTML = `
    <section class="nf-shell" data-tilt="5" aria-labelledby="nf-title">
      <span class="nf-code" aria-hidden="true">404</span>
      <span class="section-label">halaman tidak ditemukan</span>
      <h2 id="nf-title">Halaman ini tidak ada.</h2>
      <p>Mungkin link-nya salah ketik, atau halamannya sudah dipindah. Coba mulai lagi dari salah satu halaman di bawah.</p>
      <div class="result-actions">
        <a href="#/scan" class="button button-primary">Periksa link</a>
        <a href="#/" class="button">Kembali ke Home</a>
      </div>
    </section>
  `;
  enableTilt(root);
}
