export function renderHome(root) {
  root.innerHTML = `
    <div class="landing-page">
      <section class="landing-hero" aria-labelledby="home-title">
        <div class="landing-intro">
          <span class="landing-kicker"><span class="status-dot"></span> Teman cek fakta digitalmu</span>
          <h1 id="home-title">Berita viral?<br><span>Cek faktanya.</span></h1>
          <p>Periksa sebuah artikel dengan satu link. HoaxScan menganalisis isi dan konteksnya agar kamu bisa menilai informasi dengan lebih yakin.</p>
          <ul class="landing-benefits" aria-label="Keunggulan HoaxScan">
            <li>Analisis 3 modalitas</li>
            <li>Hasil dalam hitungan detik</li>
            <li>Skor dan alasan yang transparan</li>
          </ul>
        </div>

        <div class="paper-card quick-check-card">
          <span class="paper-tab tab-blue">mulai pemeriksaan</span>
          <div class="quick-card-top"><span class="tiny-stamp">01</span><span class="mono-label">PEMERIKSAAN LINK</span></div>
          <form id="quick-scan-form">
            <label for="quick-scan-url">Link artikel berita</label>
            <div class="quick-input-row">
              <input id="quick-scan-url" name="url" type="url" placeholder="https://media.id/berita/..." autocomplete="url" required>
              <button class="button button-primary" type="submit">Periksa </button>
            </div>
            <p class="quick-note">Saat ini mendukung artikel berbahasa Indonesia.</p>
          </form>
          <div class="paper-card-bottom"><span class="status-dot"></span> Cukup masukkan link artikel. Tidak perlu menyalin isi berita.</div>
        </div>

        <div class="landing-seal" aria-hidden="true"><span>H</span><small>SCAN<br>SMART</small></div>
      </section>

      <section class="landing-how">
        <div class="how-heading">
          <span class="mono-label">VERIFIKASI YANG LEBIH MUDAH</span>
          <h2>Mulai dari link, pahami hasilnya.</h2>
        </div>
        <div class="how-grid">
          <article class="how-card"><span class="how-number">01</span><h3>Masukkan link</h3><p>Salin alamat lengkap artikel yang ingin kamu periksa.</p></article>
          <article class="how-card"><span class="how-number">02</span><h3>Tunggu analisis</h3><p>HoaxScan membaca artikel dari link yang kamu kirim.</p></article>
          <article class="how-card"><span class="how-number">03</span><h3>Tinjau hasil</h3><p>Pahami penilaian, skor, alasan, dan rujukan yang tersedia.</p></article>
        </div>
      </section>

      <section class="home-signals" aria-labelledby="signals-title">
        <div class="signals-heading">
          <span class="mono-label">JADI PEMBACA YANG LEBIH TELITI</span>
          <h2 id="signals-title">Sebelum percaya, cek dulu sinyalnya.</h2>
          <p>Gunakan hasil analisis sebagai titik awal. Kebiasaan sederhana ini juga membantu kamu menilai sebuah berita dengan lebih cermat.</p>
        </div>
        <div class="signals-grid">
          <article class="signal-card signal-source">
            <span class="signal-icon" aria-hidden="true">↗</span>
            <span class="signal-tag">SUMBER</span>
            <h3>Siapa yang menerbitkan?</h3>
            <p>Periksa nama media, penulis, dan apakah informasi serupa dilaporkan sumber tepercaya lain.</p>
          </article>
          <article class="signal-card signal-context">
            <span class="signal-icon" aria-hidden="true">◷</span>
            <span class="signal-tag">KONTEKS</span>
            <h3>Kapan dan di mana?</h3>
            <p>Pastikan tanggal, lokasi, foto, dan kutipan sesuai dengan peristiwa yang sedang dibahas.</p>
          </article>
          <article class="signal-card signal-language">
            <span class="signal-icon" aria-hidden="true">Aa</span>
            <span class="signal-tag">ISI</span>
            <h3>Apakah judulnya berlebihan?</h3>
            <p>Waspadai judul yang memancing emosi atau mendesak kamu untuk segera menyebarkan berita.</p>
          </article>
        </div>
      </section>

      <section class="home-reminder" aria-label="Pengingat cek fakta">
        <div class="reminder-sticker" aria-hidden="true">!</div>
        <div class="reminder-copy">
          <span class="mono-label">BAGIKAN DENGAN BIJAK</span>
          <h2>Hasil analisis adalah bantuan, bukan pengganti penilaianmu.</h2>
          <p>Baca alasan dan rujukan yang tersedia, lalu bandingkan dengan sumber lain sebelum mengambil keputusan.</p>
        </div>
        <a class="button button-dark" href="#/history">Lihat riwayat</a>
      </section>

      <section class="landing-bottom-note">
        <div><span class="mono-label">PERIKSA SEBELUM MEMBAGIKAN</span><h2>Informasi yang baik dimulai dari cek fakta.</h2></div>
        <a class="text-link" href="#/scan">Lanjut ke pemeriksaan</a>
      </section>
    </div>
  `;

  root.querySelector("#quick-scan-form").addEventListener("submit", (event) => {
    event.preventDefault();
    const url = root.querySelector("#quick-scan-url").value.trim();
    sessionStorage.setItem("hoaxscan_pending_url", url);

    window.location.hash = "#/scan";
  });
}
