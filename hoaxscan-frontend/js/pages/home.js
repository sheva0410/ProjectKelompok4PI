export function renderHome(root) {
  root.innerHTML = `
    <div class="hm-page">
      <section class="hm-hero" aria-labelledby="home-title">
        <div class="hm-hero-copy">
          <span class="hm-eyebrow">HoaxScan</span>
          <h1 id="home-title">Curiga sama berita yang lagi viral? <span>Cek dulu.</span></h1>
          <p>HoaxScan membaca artikel dari link yang kamu tempel, lalu menilai apakah isinya cenderung hoaks, fakta, atau belum bisa dipastikan. Alasannya ikut ditampilkan, jadi kamu tahu kenapa hasilnya begitu.</p>
          <div class="hm-actions">
            <a class="button button-primary" href="#/scan">Periksa sebuah link</a>
            <a class="button" href="#/history">Lihat riwayat</a>
          </div>
        </div>

        <figure class="hm-sample" aria-label="Contoh tampilan hasil pemeriksaan">
          <span class="hm-sample-tag">contoh tampilan hasil</span>
          <div class="hm-ring" style="--pct:87"><b>87%</b></div>
          <span class="hm-verdict">Terindikasi hoax</span>
          <ul class="hm-chips" aria-label="Bagian yang dinilai">
            <li class="on">✓ Teks</li>
            <li>– Gambar</li>
            <li>– Video</li>
          </ul>
          <figcaption>Domain tidak terdaftar sebagai media terverifikasi, dan pola URL mirip situs yang pernah menyebarkan klaim tanpa dasar.</figcaption>
        </figure>
      </section>

      <section class="hm-facts" aria-label="Tentang HoaxScan">
        <div><b>Berbahasa Indonesia</b><p>Dibuat untuk artikel berita berbahasa Indonesia.</p></div>
        <div><b>Cukup satu link</b><p>Tidak perlu menyalin isi berita satu per satu.</p></div>
        <div><b>Ada alasannya</b><p>Hasilnya disertai penjelasan, bukan cuma label.</p></div>
      </section>

      <section class="hm-section" aria-labelledby="how-title">
        <div class="hm-head">
          <span class="hm-eyebrow">cara kerjanya</span>
          <h2 id="how-title">Dari link sampai hasil, empat langkah.</h2>
        </div>
        <ol class="hm-steps">
          <li><span>1</span><h3>Tempel link</h3><p>Salin alamat lengkap artikelnya, lalu tempel di halaman Periksa link.</p></li>
          <li><span>2</span><h3>Artikel dibaca</h3><p>HoaxScan mengambil judul dan isi artikel dari halaman tersebut.</p></li>
          <li><span>3</span><h3>Dinilai</h3><p>Isinya dinilai, lalu keluar label dan skor keyakinan.</p></li>
          <li><span>4</span><h3>Kamu yang memutuskan</h3><p>Baca alasannya, lalu bandingkan dengan sumber lain sebelum percaya.</p></li>
        </ol>
      </section>

      <section class="hm-section" aria-labelledby="result-title">
        <div class="hm-head">
          <span class="hm-eyebrow">isi hasilnya</span>
          <h2 id="result-title">Yang akan kamu lihat setelah memeriksa.</h2>
        </div>
        <div class="hm-cards">
          <article class="hm-card hm-yellow">
            <h3>Label</h3>
            <p>Salah satu dari <em>terindikasi hoax</em>, <em>cenderung kredibel</em>, atau <em>tidak pasti</em>.</p>
          </article>
          <article class="hm-card hm-mint">
            <h3>Skor keyakinan</h3>
            <p>Seberapa yakin sistem dengan penilaiannya, dalam persen. Makin tinggi bukan berarti pasti benar.</p>
          </article>
          <article class="hm-card hm-pink">
            <h3>Alasan</h3>
            <p>Penjelasan singkat kenapa artikel dinilai begitu, plus rujukan kalau tersedia.</p>
          </article>
          <article class="hm-card hm-blue">
            <h3>Bagian yang dinilai</h3>
            <p>Lencana teks, gambar, dan video menunjukkan mana yang sudah ikut diperiksa dan mana yang belum.</p>
          </article>
        </div>
      </section>

      <section class="hm-section" aria-labelledby="tips-title">
        <div class="hm-head">
          <span class="hm-eyebrow">kebiasaan kecil</span>
          <h2 id="tips-title">Sebelum membagikan berita, cek tiga hal ini.</h2>
        </div>
        <ul class="hm-tips">
          <li><b>Siapa yang menerbitkan?</b><span>Lihat nama medianya dan apakah media lain melaporkan hal yang sama.</span></li>
          <li><b>Kapan dan di mana?</b><span>Foto atau kutipan lama sering dipakai ulang seolah baru kejadian.</span></li>
          <li><b>Judulnya bikin emosi?</b><span>Judul yang menyuruh kamu buru-buru menyebarkan patut dicurigai.</span></li>
        </ul>
      </section>

      <aside class="hm-note" aria-label="Batasan HoaxScan">
        <b>Soal batasan</b>
        <p>Hasil HoaxScan itu petunjuk awal, bukan putusan akhir. Sistem bisa salah, terutama untuk berita yang baru muncul. Kalau masih ragu, cocokkan dengan media yang kredibel.</p>
      </aside>

      <section class="hm-cta">
        <h2>Ada link yang mau dicek?</h2>
        <a class="button button-primary" href="#/scan">Periksa sekarang</a>
      </section>
    </div>
  `;
}
