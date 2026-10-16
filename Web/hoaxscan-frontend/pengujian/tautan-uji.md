# Daftar tautan uji HoaxScan (FE-09)

Bahan pengujian ujung ke ujung (FE-05). HoaxScan menerima link artikel dan menilai isinya, baik artikel
yang hanya berisi teks, teks dengan gambar, maupun teks dengan video. Karena itu 15 tautan di bawah
dibagi menurut isi artikelnya:

| Kelompok | Jumlah | Tujuan |
|---|---|---|
| Hanya teks | 3 | Artikel tanpa gambar dan video sama sekali |
| Teks + gambar | 4 | Termasuk satu infografik yang isinya terutama gambar |
| Teks + video | 4 | Video tertanam di halaman |
| Cek fakta / hoaks | 4 | Artikel bantahan hoaks, dua di antaranya membahas video |

Semua tautan dicek pada **16 Oktober 2026** dengan `User-Agent` yang sama seperti scraper backend
(`HoaxScanBot/1.0`). Gambar dideteksi dengan aturan yang sama seperti `media.py` di backend: `og:image`,
lalu `<link rel="image_src">`, lalu `<img>` di dalam `<article>`. Versi data ada di
[`tautan-uji.json`](tautan-uji.json).

| No | Kelompok | Media | Judul | Gambar | Video | Catatan |
|---|---|---|---|---|---|---|
| 1 | Hanya teks | OJK (siaran pers) | [Siaran Pers: OJK Berkomitmen untuk Terus Melanjutkan dan Memperkuat Reformasi Pasar Modal Indonesia](https://www.ojk.go.id/id/berita-dan-kegiatan/siaran-pers/Pages/OJK-Berkomitmen-untuk-Terus-Melanjutkan-dan-Memperkuat-Reformasi-Pasar-Modal-Indonesia.aspx) | - | - |  |
| 2 | Hanya teks | OJK (siaran pers) | [Siaran Pers: Terbitkan POJK Rencana Bisnis Bank Umum, OJK Perkuat Kontribusi Perbankan dalam Pembangunan Nasional](https://www.ojk.go.id/id/berita-dan-kegiatan/siaran-pers/Pages/POJK-17-Tahun-2026-Rencana-Bisnis-Bank-Umum.aspx) | - | - |  |
| 3 | Hanya teks | OJK (siaran pers) | [Siaran Pers: OJK Cabut Izin Usaha PT Porto Ventura Kapital](https://www.ojk.go.id/id/berita-dan-kegiatan/siaran-pers/Pages/OJK-Cabut-Izin-Usaha-PT-Porto-Ventura-Kapital.aspx) | - | - |  |
| 4 | Teks + gambar | ANTARA | [Antisipasi dampak asap, Pemkot Medan terapkan PJJ hingga 21 Oktober](https://www.antaranews.com/berita/5790773/antisipasi-dampak-asap-pemkot-medan-terapkan-pjj-hingga-21-oktober) | ya | - |  |
| 5 | Teks + gambar | CNN Indonesia | [Penjelasan KPK soal OTT Klaten, Seret Kepala BPK di Jateng](https://www.cnnindonesia.com/nasional/20261016124548-16-1416109/penjelasan-kpk-soal-ott-klaten-seret-kepala-bpk-di-jateng) | ya | - | Peristiwa sama dengan tautan 6 dan 8 (OTT Klaten). |
| 6 | Teks + gambar | detikcom | [5 Fakta Terkini OTT Bupati Klaten: Barbuk Rp 1 M, Puluhan Orang Ditangkap](https://news.detik.com/berita/d-8709387/5-fakta-terkini-ott-bupati-klaten-barbuk-rp-1-m-puluhan-orang-ditangkap) | ya | - | Peristiwa sama dengan tautan 5 dan 8 (OTT Klaten). |
| 7 | Teks + gambar | Kompas.com (Cek Fakta) | [INFOGRAFIK: Muncul Hoaks Bola Es Raksasa Jatuh dari Langit, Video Itu Konten AI](https://www.kompas.com/cekfakta/read/2026/10/15/155000082/infografik--muncul-hoaks-bola-es-raksasa-jatuh-dari-langit-video-itu) | ya | - | Isinya terutama gambar infografik. |
| 8 | Teks + video | ANTARA | [KPK amankan 20 orang termasuk bupati melalui OTT di Klaten](https://www.antaranews.com/berita/5790153/kpk-amankan-20-orang-termasuk-bupati-melalui-ott-di-klaten) | ya | ya | Peristiwa sama dengan tautan 5 dan 6 (OTT Klaten). |
| 9 | Teks + video | ANTARA | [Danantara berkomitmen salurkan Rp1,7 T di kesehatan hingga pendidikan](https://www.antaranews.com/berita/5790169/danantara-berkomitmen-salurkan-rp17-t-di-kesehatan-hingga-pendidikan) | ya | ya |  |
| 10 | Teks + video | ANTARA | [Hadapi tantangan cuaca, Para Panahan tetap bidik dua medali emas](https://asiangames.antaranews.com/berita/5790209/hadapi-tantangan-cuaca-para-panahan-tetap-bidik-dua-medali-emas) | ya | ya |  |
| 11 | Teks + video | 20detik | [Video: Ledakan Dahsyat di Pasar Cimanggis Berasal dari Ruang Pematangan Buah](https://20.detik.com/detikupdate/20261015-261015043/video-ledakan-dahsyat-di-pasar-cimanggis-berasal-dari-ruang-pematangan-buah) | ya | ya | Kasus perbatasan: teks hanya sekitar 300 karakter. |
| 12 | Cek fakta / hoaks | Kompas.com (Cek Fakta) | [[HOAKS] Prabowo Tunjuk AHY Sebagai Wapres pada September 2026](https://www.kompas.com/cekfakta/read/2026/10/16/092838282/hoaks-prabowo-tunjuk-ahy-sebagai-wapres-pada-september-2026) | ya | - |  |
| 13 | Cek fakta / hoaks | Kompas.com (Cek Fakta) | [[KLARIFIKASI] Video AI, Rocky Gerung Bungkam Ditanya Keinginannya agar Gibran Mundur](https://www.kompas.com/cekfakta/read/2026/10/15/165600782/-klarifikasi-video-ai-rocky-gerung-bungkam-ditanya-keinginannya-agar) | ya | - | Membahas video buatan AI, tapi videonya tidak tertanam di halaman. |
| 14 | Cek fakta / hoaks | TurnBackHoax (Mafindo) | [[SALAH] Wapres Gibran Mengundurkan Diri](https://turnbackhoax.id/articles/37210-salah-wapres-gibran-mengundurkan-diri) | ya | - |  |
| 15 | Cek fakta / hoaks | TurnBackHoax (Mafindo) | [[SALAH] Video Pertahanan Udara Arab Saudi Cegat Drone Houthi di Makkah September 2026](https://turnbackhoax.id/articles/37209-salah-video-pertahanan-udara-arab-saudi-cegat-drone-houthi-di-makkah-september-2026) | ya | - | Membahas video, tapi videonya tidak tertanam di halaman. |

## Hasil yang diharapkan

- **Saat ini** (modul AI masih stub): semua tautan seharusnya selesai dengan status `done` dan label
  *Tidak pasti 0%*, dengan lencana modalitas kosong. Yang diuji adalah alurnya: tahapan status, judul
  artikel, pesan galat, riwayat, dan tren.
- **Setelah modul AI terpasang**, lencana modalitas seharusnya mengikuti isi artikel: kelompok *hanya teks*
  hanya *Teks*, kelompok *teks + gambar* menyertakan *Gambar*, dan kelompok *teks + video* menyertakan *Video*.
  Kolom `modalitas_seharusnya` di file JSON mencatat harapan ini.
- **Label kelompok cek fakta perlu disepakati tim:** artikelnya sendiri adalah bantahan yang kredibel, tetapi
  isinya membahas klaim hoaks. Apakah HoaxScan menilai artikelnya (*fakta*) atau klaim yang dibahas (*hoax*)?
- **Tautan 11 (20detik)** adalah kasus perbatasan: teksnya hanya sekitar 300 karakter, dekat batas minimum
  backend (200 karakter). Bisa lolos, atau ditolak dengan pesan *Isi artikel tidak ditemukan*. Keduanya dicatat.

## Catatan

- Artikel yang benar-benar tanpa gambar jarang ditemukan, karena hampir semua situs berita memasang gambar
  utama. Dari beberapa situs yang dicek (OJK, BPOM, Setkab, dll.), hanya siaran pers OJK yang lolos, jadi ketiga
  tautan *hanya teks* berasal dari OJK.
- Tautan 5, 6, dan 8 membahas peristiwa yang sama (OTT Bupati Klaten) dari tiga media dan dua jenis isi. Berguna
  untuk membandingkan konsistensi hasil setelah AI terpasang.
- Berita bisa dihapus atau dipindah. Kalau ada tautan yang mati saat pengujian, ganti dengan artikel sejenis dari
  media dan kelompok yang sama, lalu catat perubahannya.

## Cadangan untuk FE-06 (uji negatif)

Ditemukan saat mengumpulkan tautan, belum termasuk 15 tautan di atas:

- **Tempo menolak bot:** artikel `nasional.tempo.co/read/...` membalas **HTTP 403** ke `HoaxScanBot`. Cocok untuk
  uji *situs terblokir*. Contoh: https://nasional.tempo.co/read/2121699/satgas-prr-bikin-sumur-bor-untuk-warga-terdampak-banjir-aceh-utara
- **Halaman video CNN TV:** videonya dimuat lewat JavaScript sehingga tidak terdeteksi sebagai video. Cocok untuk
  uji *media yang tidak terbaca*. Contoh: https://www.cnnindonesia.com/tv/20261016115359-402-1416089/video-ihsg-ambles-10-msci-mau-downgrade
- **Situs yang menolak bot lainnya:** infopublik.id, mkri.id, dan komdigi.go.id membalas **HTTP 403**.
