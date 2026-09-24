# Interconnecting between Digital Awareness and Application Design

| | |
|---|---|
| **Nama** | Naufal Alfathan Hafizh |
| **NIM** | 24782088 |
| **Kelas** | C |
| **Proyek Kelompok** | HoaxScan |

---

## Bagian 1. Identitas dan Topik Proyek Aplikasi

**Nama aplikasi.** HoaxScan
*Sistem Pendeteksi Berita Hoax Berbasis Kecerdasan Buatan Hybrid dengan Analisis Multimodal Teks, Gambar, dan Video*

**Status proyek.** HoaxScan masih tahap rancangan, jadi semua uraian di laporan ini menyatakan apa yang dirancang.

**Deskripsi dan tujuan.** HoaxScan dirancang menerima satu link berita, lalu melakukan scraping terhadap teks artikel, gambar, dan video di halaman itu. Penilaiannya berjalan dalam dua tahap. IndoBERT membaca teks secara lokal tanpa biaya per request, sedangkan Gemini dipanggil ketika halaman memuat gambar atau video, atau ketika IndoBERT ragu terhadap teksnya. Gemini menilai gambar dan videonya, lalu membandingkan klaim dengan rujukan fact-check hasil RAG retrieval. Outputnya berupa label (Hoax, Fakta, atau Tidak Pasti), confidence score, penjelasan berbahasa Indonesia, dan daftar sumber rujukan yang bisa diklik.

**Masalah yang diselesaikan.** Satu link berita bisa membawa klaim tertulis, foto dari peristiwa lain, dan video yang sudah dipotong konteksnya sekaligus. Alat yang hanya membaca teks tidak akan menangkap manipulasi di gambar dan video. Masalah keduanya, label saja tidak cukup bagi pengguna awam karena mereka tidak punya bahan untuk menilai ulang. HoaxScan dirancang selalu menyertakan alasan beserta sumbernya, termasuk mengakui ketika rujukannya belum memadai.

**Target pengguna.** Warga yang menerima link mencurigakan lewat WhatsApp atau social media dan ingin mengecek sebelum ikut menyebarkan. Alur registrasinya direncanakan sesingkat mungkin supaya mereka cepat mendapat hasil. Pengguna kedua adalah jurnalis dan pegiat fact-check yang butuh triase cepat sebelum melakukan verifikasi manual.

---

## Bagian 2. Resume Modul Digital Awareness

### Modul 1. There's a whole new world out there!

Perpindahan dari analog ke digital membawa untung sekaligus rugi. Di satu sisi ada GPS, video call lintas benua, dan pembayaran tagihan dalam beberapa klik. Di sisi lain ada screen time berlebih, risiko data pribadi disalahgunakan, dan digital divide antara yang punya akses dan yang tidak. Ada tiga digital environment yang perlu dikenali sebelum mulai, yaitu operating system sebagai fondasi, browser sebagai pintu masuk internet, dan aplikasi sebagai alat kerja spesifik. Internet tahun 1990-an hampir seluruhnya teks sampai Web 2.0 membuatnya bisa diajak berbalas, lalu IoT melangkah lebih jauh dengan menyambungkan benda sehari-hari ke internet. Online service terbagi menjadi public (website pemerintah, platform pendidikan), private (e-commerce, online banking, subscription), dan community-based (social media, Wikipedia, Project Gutenberg).

### Modul 2. You'll Need Some Basic Tools

Tidak ada aplikasi yang jalan tanpa operating system, yang sekaligus menyediakan graphical interface dan menata file kita. Input device mengirim informasi ke komputer, output device mengembalikannya ke kita, dan sambungannya lewat USB, HDMI, atau Bluetooth yang jangkauannya cuma sekitar sepuluh meter. Inti modul ini ada di manajemen file. Desktop cepat berantakan kalau dipakai menampung segalanya, jadi folder dengan penataan yang masuk akal jauh lebih berguna. Penamaan file juga menentukan. Isi folder hanya memperlihatkan nama, format, tanggal, dan ukurannya, bukan isinya, dan modul mengumpamakannya seperti rak buku yang semua punggungnya kosong sehingga tiap buku harus dibuka satu per satu.

### Modul 3. This is how you get around and find what you're looking for

Search engine bekerja dari teks yang kita ketik, dan hasilnya bisa dipersempit lewat search operator. Tanda kutip mengunci frasa persis, tanda minus membuang kata tertentu, operator site mengunci pencarian ke satu website, dan operator filetype menyaring jenis file. Pencarian di dalam dokumen ditangani Ctrl+F. Cookie menyimpan preferensi bahasa, status login, dan isi shopping cart, tapi advertiser juga memakainya untuk tracking, dan di situlah keberatan privasi muncul. Bagian terpanjang modul ini membahas copyright. Perlindungan berlaku otomatis begitu karya berwujud, Creative Commons menawarkan jalan tengah dari CC BY sampai CC BY-NC-ND, dan public domain bebas dipakai siapa saja (tokoh Winnie the Pooh versi buku sejak 2022, sedangkan versi Disney tetap terlindungi). Fair use punya patokan kasar di bawah sepuluh persen, dan software copyright menaungi lisensi open source.

### Modul 4. It just keeps getting better

Istilah artificial intelligence lahir di Dartmouth College pada 1956, lalu berkembang lewat expert system, neural network, sampai Large Language Model yang sanggup memahami dan menghasilkan teks menyerupai tulisan manusia. Sikap modul soal etika tegas. AI tidak baik atau buruk dengan sendirinya, dan hasilnya ditentukan rancangan, dataset latih, serta niat penerapnya, sehingga bias manusia gampang menyelinap masuk. Netiquette bertumpu pada satu hal, yaitu ada manusia sungguhan di seberang layar. Digital addiction ditandai hilangnya kendali dan dilawan dengan membatasi screen time serta mematikan push notification yang tidak perlu. Soal misinformation, modul mengingatkan bahwa jumlah view, share, atau like tidak membuktikan apa pun, jadi verifikasi ke beberapa sumber kredibel tetap wajib sebelum ikut menyebarkan.

### Modul 5. Even Though It's Digital, It is Real, With Real Consequences

Digital persona terbagi menjadi professional, social, dan consumer, semuanya terbentuk dari jejak yang kita tinggalkan sendiri. Tema utamanya permanence. Menghapus postingan itu gampang, masalahnya menyalin sama gampangnya, sehingga foto yang sudah dihapus bisa terus hidup di tempat yang tidak pernah kita ketahui. Online anonymity melindungi whistleblower dan orang yang mencari bantuan untuk masalah sensitif, tapi juga memayungi pelaku cyberbullying dan troll. VPN menyamarkan IP address, sedangkan incognito mode menyembunyikan browsing history dari orang yang memakai komputer setelah kita. Menghadapi pesan kasar, modul menyarankan jeda sebelum membalas, dan troll paling ampuh diabaikan. Korban cyberbullying dianjurkan tidak membalas, menyimpan bukti, mem-block pelaku, lalu melapor. FBI Internet Crime Report 2022 mencatat potensi kerugian lebih dari 10,2 miliar dolar dari phishing, identity theft, romance scam, sampai pig butchering.

### Modul 6. Learn About Anything and Everything

Troubleshooting dikerjakan berurutan, bukan asal tebak. Cek power source lebih dulu, bebaskan storage dan tutup aplikasi background untuk perangkat yang melambat, uji network memakai perangkat lain sebelum menyalahkan router, dan periksa file extension saat file enggan terbuka. File converter online memang membantu, tapi file-nya harus di-upload lebih dulu sehingga tidak cocok untuk dokumen sensitif. Untuk menutup skills gap tersedia banyak jalan, mulai dari kursus seperti Cisco Networking Academy dan OpenEDG Edube, video tutorial YouTube, MOOC universitas yang sebagian menawarkan gelar penuh, e-book, webinar gratis, sampai forum komunitas tempat jawaban terbaik naik ke puncak lewat upvote.

---

## Bagian 3. Hubungan dan Implementasi pada Topik Proyek

### Pertanyaan 1

> **Soal.** Bagaimana rancangan aplikasi dapat mempermudah tugas sehari-hari pengguna? Apa proses "analog/tradisional" dari topik proyekmu yang berhasil disederhanakan menjadi digital?

**Jawaban.**

Proses tradisional yang ingin disederhanakan adalah verifikasi berita secara manual. Orang yang menerima link mencurigakan harus membaca artikelnya, menyalin klaim utamanya ke search engine, membuka beberapa hasil pencarian, mencocokkannya dengan situs cek fakta seperti Turnbackhoax, lalu menilai sendiri apakah foto dan videonya benar berasal dari peristiwa yang dimaksud. Setiap langkah dikerjakan manusia satu per satu, dan orang itu harus tahu lebih dulu sumber mana yang layak dipercaya.

HoaxScan dirancang memampatkan rangkaian itu menjadi satu tindakan, yaitu menempel link lalu membaca hasilnya. Pencocokan ke arsip cek fakta dikerjakan RAG retrieval yang mencari rujukan dengan makna paling dekat ke klaim, sedangkan pemeriksaan foto dan video diserahkan ke Gemini. Hasilnya berupa label, confidence score, penjelasan, dan link sumber. Targetnya, link tanpa media selesai dalam kurang dari 5 detik dan link bergambar dalam kurang dari 15 detik.

Aplikasi ini memangkas waktu penyaringan awal dan tidak menggantikan verifikasi manual. Label Tidak Pasti disediakan untuk kasus yang memang belum bisa diputuskan.

### Pertanyaan 2

> **Soal.** Jika aplikasimu memiliki fitur penyimpanan file atau pendaftaran akun, bagaimana kamu merancang struktur penyimpanan file yang intuitif bagi pengguna awam? Bagaimana kamu membantu pengguna membuat kata sandi yang aman?

**Jawaban.**

HoaxScan direncanakan punya registrasi dan login akun, tetapi tidak menerima upload file karena inputnya hanya link. Yang perlu ditata adalah riwayat pemeriksaan tiap akun.

Struktur riwayatnya meminjam prinsip penamaan dari Modul 2, yaitu isi harus bisa dikenali tanpa dibuka. Tiap baris menampilkan judul artikel, bukan URL mentah, karena alamat seperti `kompas.com/read/2026/xxxxxxx` tidak memberi tahu apa-apa. Di sebelah judul ada label, confidence score, dan waktu pemeriksaan, diurutkan dari yang terbaru. Cara mencari di riwayat dijelaskan di Pertanyaan 3. Riwayat dirancang terpisah per akun supaya link yang diperiksa seseorang tidak terlihat oleh pengguna lain.

Untuk password, Modul 5 menganjurkan password yang kuat dan unik untuk tiap akun, pemakaian password manager, dan two-factor authentication bila tersedia. Panduan NIST SP 800-63B menganjurkan agar tidak mewajibkan campuran huruf besar, angka, dan simbol, tidak memaksa penggantian berkala, mengutamakan panjang, dan mengecek password baru terhadap daftar password yang pernah bocor. Form pendaftaran dirancang menampilkan indikator kekuatan password beserta alasannya, misalnya "terlalu pendek". Password tidak disimpan dalam bentuk asli. Ia di-hash, dengan bcrypt sebagai kandidat algoritmanya.

### Pertanyaan 3

> **Soal.** Bagaimana kamu mendesain fitur pencarian (search bar) di dalam aplikasi agar pengguna dapat mencari informasi dengan mudah? Selain itu, sebutkan asset eksternal yang digunakan dalam aplikasi (library, API, gambar, icon). Apakah asset-aset tersebut berlisensi open-source, public domain, atau memiliki hak cipta khusus yang wajib dicantumkan?

**Jawaban.**

HoaxScan dirancang punya satu search bar, di halaman riwayat pemeriksaan.

Search bar riwayat mencari berdasarkan judul artikel atau nama situs, dan hasilnya bisa dipersempit dengan filter label (Hoax, Fakta, Tidak Pasti) serta rentang waktu. Rancangan ini mengikuti Modul 3. Search engine membiarkan pengguna mempersempit hasil lewat jenis dan rentang waktu, jadi filter label berperan seperti pilihan jenis hasil dan rentang waktu seperti menu Tools. Placeholder-nya menyebut cakupan pencarian ("Cari judul atau nama situs"), dan kalau tidak ada yang cocok, yang tampil adalah pesan dengan tombol untuk menghapus pencarian, bukan tabel kosong.

Asset eksternal yang direncanakan beserta lisensinya ada di tabel berikut. Versi dan lisensi dibaca dari metadata paket yang terpasang di mesin pengembangan, kecuali `transformers`, `sentence-transformers`, `bcrypt`, dan kedua model yang diambil dari PyPI atau HuggingFace karena belum terpasang.

| Asset | Jenis | Fungsi | Lisensi | Kategori |
|---|---|---|---|---|
| FastAPI 0.141.1 | library | web framework | MIT | open source |
| Uvicorn 0.52.4 | library | ASGI server | BSD-3-Clause | open source |
| SQLAlchemy 2.0.41 | library | ORM database | MIT | open source |
| Pydantic 2.13.5 | library | validasi skema API | MIT | open source |
| Jinja2 3.1.6 | library | template HTML | BSD | open source |
| newspaper3k 0.2.8 | library | ekstraksi teks dan metadata artikel, serta penemuan gambar utama dan video di halaman | MIT | open source |
| lxml_html_clean 0.4.5 | library | dependensi yang dibutuhkan newspaper3k agar bisa berjalan | BSD-3-Clause | open source |
| requests 2.32.5 | library | men-download HTML dan gambar | Apache-2.0 | open source |
| yt-dlp 2026.8.19 | library | download file video | Unlicense | public domain |
| FFmpeg 8.0.1 | program eksternal | dipanggil yt-dlp untuk menggabungkan stream video | GPL v3 (pada build yang terpasang) | open source, dijalankan sebagai program terpisah |
| langdetect 1.0.9 | library | deteksi bahasa | MIT | open source |
| PyTorch 2.9.1 | library | runtime IndoBERT | BSD-3-Clause | open source |
| transformers 5.17.0 | library | memuat dan menjalankan IndoBERT, sekaligus fine-tuning | Apache-2.0 | open source |
| sentence-transformers 6.1.0 | library | menjalankan model embedding untuk RAG retrieval | Apache-2.0 | open source |
| pandas 2.3.3 | library | membaca dan membersihkan dataset latih | BSD-3-Clause | open source |
| scikit-learn 1.7.2 | library | pembagian data dan metrik F1 per kelas untuk evaluasi | BSD-3-Clause | open source |
| google-genai 2.23.0 | library | SDK Gemini | Apache-2.0 | open source |
| python-dotenv 1.2.2 | library | membaca API key dan konfigurasi dari file `.env` | BSD-3-Clause | open source |
| bcrypt 5.0.0 | library | hash password (kandidat, belum diputuskan) | Apache-2.0 | open source |
| IndoBERT `indobert-base-p1` | model AI | classifier teks | MIT | open source, model card meminta sitasi |
| `paraphrase-multilingual-MiniLM-L12-v2` | model AI | embedding untuk RAG retrieval | Apache-2.0 | open source |
| Gemini API | API | penilai multimodal | Gemini API Additional Terms of Service | proprietary, bukan open source |
| Dataset Kaggle "Indonesian Fact and Hoax Political News" | dataset | data latih classifier | MIT menurut deskripsi dataset (kolom lisensi Kaggle berisi "Other") | open source, konten artikelnya tetap milik media asal |
| Gambar dan icon | - | - | belum ditentukan | bila dipakai, lisensinya dicantumkan |

Tugas antar library sengaja tidak dibagi ke lebih dari satu library. `requests` satu-satunya yang men-download HTML dan gambar, `newspaper3k` satu-satunya yang mengekstrak teks sekaligus mencari gambar dan video, dan `yt-dlp` satu-satunya yang men-download video.

Lisensi permisif seperti MIT, BSD, dan Apache-2.0 umumnya mengizinkan pemakaian bebas, dengan kewajiban menyertakan pemberitahuan lisensi bila kodenya didistribusikan ulang. yt-dlp memakai Unlicense, yaitu pelepasan ke public domain. FFmpeg di mesin pengembangan adalah build GPL v3, tetapi hanya dipanggil yt-dlp sebagai program terpisah dan tidak digabung ke kode HoaxScan. Model card IndoBERT meminta pemakainya mencantumkan sitasi kepada penciptanya, jadi sitasi itu akan masuk daftar pustaka. Gemini bukan open source. Ia layanan Google yang tunduk pada Gemini API Additional Terms of Service. Pada free tier, syarat itu menyatakan bahwa input dan output boleh dibaca oleh human reviewer untuk meningkatkan produk Google, bahwa data sensitif, rahasia, atau pribadi tidak boleh dikirim, dan bahwa layanan tidak boleh dipakai di aplikasi yang ditujukan untuk atau kemungkinan besar diakses pengguna di bawah 18 tahun. Pada paid tier, Google menyatakan tidak memakai prompt dan respons untuk meningkatkan produknya.

Dataset Kaggle mencantumkan "Other (specified in description)" di kolom lisensinya, dan deskripsinya menyebut MIT License. Lisensi itu dipasang oleh pengunggah dataset. Artikelnya sendiri diambil dari CNN Indonesia, Kompas, Tempo, dan Turnbackhoax, yang hak ciptanya belum tentu ikut dilepas oleh pengunggah, jadi dataset dipakai untuk melatih model dan artikelnya tidak ditampilkan ulang. Untuk gambar dan icon belum ada keputusan.

### Pertanyaan 4

> **Soal.** Jika aplikasimu memiliki fitur interaksi sosial, bagaimana kamu mencegah pelanggaran etika digital di dalamnya? Jika aplikasi menggunakan fitur pintar berbasis AI, bagaimana kamu memastikan AI tersebut bekerja secara etis dan bertanggung jawab bagi pengguna?

**Jawaban.**

HoaxScan tidak dirancang punya interaksi sosial. Akunnya pribadi, tanpa kolom komentar, profil yang bisa dilihat pengguna lain, ataupun pesan antar pengguna. Alasannya, kolom komentar di aplikasi pemeriksa hoax akan mengundang trolling dan penyebaran klaim baru yang tidak diperiksa siapa pun, sedangkan tanpa ruang sosial tidak ada yang perlu dimoderasi.

Untuk AI-nya, Modul 4 menyatakan teknologi tidak netral karena pembuatannya dipengaruhi pandangan yang berlaku saat itu, dan bias bisa masuk lewat data latih. Dataset yang direncanakan berisi artikel fakta dari CNN Indonesia, Kompas, dan Tempo, serta artikel hoax dari klarifikasi Turnbackhoax, dengan jumlah artikel fakta jauh lebih banyak daripada hoax. Sumber yang seragam untuk tiap kelas menimbulkan kemungkinan bahwa model belajar mengenali gaya penulisan media dan bukan kebenaran isinya, sehingga berita benar dari situs kecil ikut tertandai hoax. Kemungkinan ini belum bisa diuji karena IndoBERT belum dilatih.

Langkah yang sudah ditetapkan untuk menjaganya cukup jelas. F1 dilaporkan per kelas, bukan hanya akurasi total, karena pada data timpang akurasi tinggi bisa didapat cuma dengan menebak kelas mayoritas. Setiap hasil menyertakan penjelasan dan sumber rujukan supaya pengguna bisa menilai ulang. Ketidakpastian ditampilkan lewat label Tidak Pasti, dan jawaban Gemini "rujukan belum memadai" tidak dihitung sebagai tuduhan hoax. Kalau Gemini gagal menjawab, sistem memakai hasil classifier dan menuliskan alasannya.

Dua hal lain masih usulan. UI menyebut hasil sebagai alat bantu penyaringan dan bukan putusan akhir, dan pengguna diberi tahu bahwa isi artikel, gambar, dan video dikirim ke server Google saat Gemini dipanggil. Video yang di-upload dirancang dihapus dari server Google setelah penilaian selesai, dan file video tidak masuk database. Pada free tier, Google menyatakan input dan output boleh dibaca human reviewer, jadi pemberitahuan tadi harus menyebut hal itu. Pemakaian paid tier menghilangkan pemakaian data untuk meningkatkan produk Google, dan itu pilihan bila aplikasi dipakai luas.

### Pertanyaan 5

> **Soal.** Data pribadi sensitif (PII) apa saja yang dikumpulkan oleh aplikasimu? Bagaimana cara kamu melindungi data tersebut agar tidak bocor atau disalahgunakan? Bagaimana aplikasi meminimalkan risiko pengguna menjadi korban penipuan siber di platformmu?

**Jawaban.**

PII yang dikumpulkan direncanakan terbatas pada nama, email, dan password. Selain itu database menyimpan riwayat pemeriksaan berupa link yang ditempel, judul dan teks artikel hasil ekstraksi, alamat gambar dan video, hasil penilaian, dan waktu pemeriksaan. File video tidak disimpan. Riwayat termasuk data yang mudah diremehkan. Kumpulan link yang diperiksa seseorang bisa memperlihatkan isu yang membuatnya resah, dan begitu terikat ke akun, ia menjadi data pribadi. IP address di log server juga dapat tergolong data pribadi kalau logging diaktifkan.

Perlindungan yang sudah ditetapkan mencakup penyimpanan API key di `.env` supaya tidak masuk repository, file video yang tidak masuk database, dan penghapusan salinan video di server Google setelah penilaian. Perlindungan yang masih usulan meliputi hash password, pemeriksaan kepemilikan pada setiap request riwayat supaya id di URL tidak bisa dipakai membuka riwayat orang lain, pembatasan percobaan login untuk menjawab risiko algoritma penebak password di Modul 5, HTTPS bila aplikasi di-deploy, serta fitur menghapus riwayat dan akun sesuai saran Modul 4 untuk menghapus akun lama yang tidak dipakai.

Untuk risiko penipuan siber, halaman login adalah sasaran umum phishing. Usulannya, halaman itu menyatakan bahwa HoaxScan tidak pernah meminta password lewat email, WhatsApp, atau link dari pihak mana pun. HoaxScan juga tidak dirancang meminta uang atau data keuangan, jadi permintaan semacam itu yang mengatasnamakan HoaxScan patut dicurigai. Ada satu risiko lagi tanpa mitigasi pasti, yaitu situs penipu yang sengaja diperiksa lalu mendapat label Fakta dan dipakai sebagai seolah-olah tanda aman. Hasil pemeriksaan sebaiknya ditulis sebagai catatan bertanggal tentang apa yang diperiksa, bukan sebagai jaminan.

### Pertanyaan 6

> **Soal.** Ketika aplikasi mengalami masalah teknis (misalnya kehilangan koneksi internet atau kegagalan memuat data), bagaimana aplikasi mengomunikasikannya kepada pengguna? Tuliskan contoh rancangan pesan error ramah pengguna yang memandu pengguna melakukan troubleshooting mandiri secara mudah.

**Jawaban.**

Modul 6 mengajarkan troubleshooting yang berurutan, yaitu memeriksa sumber masalah lebih dulu baru mengambil langkah berikutnya. Pesan error HoaxScan dirancang mengikuti pola itu untuk orang yang tidak paham teknis. Setiap pesan menyebut apa yang gagal, kenapa bila diketahui, dan langkah yang bisa dicoba sendiri. Kode HTTP mentah dan stack trace tidak ditampilkan ke pengguna.

Contoh rancangan pesannya ada di tabel berikut, dengan teks di kolom kanan sebagai contoh copy yang belum final.

| Kondisi | Pesan yang tampil |
|---|---|
| Koneksi internet pengguna terputus | "Sambungan internet kamu terputus sebelum pemeriksaan selesai. Cek Wi-Fi atau data seluler, lalu tekan Periksa sekali lagi. Link yang tadi kamu tempel masih ada di kolom." |
| Riwayat gagal dimuat | "Riwayat pemeriksaanmu belum berhasil dimuat. Muat ulang halaman ini, dan kalau masih gagal, coba lagi beberapa menit lagi." |
| Situs berita menolak dibaca otomatis | "Situs ini menolak dibaca otomatis, jadi isinya tidak bisa kami ambil. Coba cari judul berita yang sama di media lain, lalu tempel link-nya ke sini." |
| Link bukan halaman artikel | "Link ini terbuka, tapi isinya bukan artikel berita. Pastikan yang kamu tempel link ke halaman beritanya, bukan halaman depan situs." |
| Format link salah | "Alamat yang ditempel belum lengkap. Link berita biasanya diawali https dan memuat nama situsnya." |
| Sesi login berakhir | "Sesi login kamu sudah berakhir. Silakan login lagi, lalu lanjutkan pemeriksaanmu." |
| Video melebihi batas durasi | "Video di halaman ini melebihi batas durasi, jadi tidak ikut diperiksa. Penilaian di bawah berdasarkan teks dan gambarnya saja." |
| Kuota Gemini harian habis | "Pemeriksaan gambar dan video sedang tidak tersedia karena jatah harian sudah terpakai. Hasil di bawah hanya berasal dari pemeriksaan teks, jadi tingkat keyakinannya lebih rendah. Coba lagi besok untuk pemeriksaan penuh." |

Dua baris pertama menjawab langsung contoh di soal, yaitu kehilangan koneksi dan kegagalan memuat data. Baris untuk situs yang menolak, halaman yang bukan artikel, dan format link yang salah menutup kegagalan saat mengambil halaman, sedangkan dua baris terakhir mengikuti rancangan bahwa kalau sebagian sistem gagal, hasil tetap diberikan dengan catatan jelas tentang bagian yang tidak sempat diperiksa. Menurut saya itu sikap yang tepat untuk aplikasi yang tugasnya melawan informasi menyesatkan, karena skor yang tampak yakin padahal sebagian pemeriksaan gagal justru menyesatkan.
