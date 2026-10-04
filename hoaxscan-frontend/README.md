# HoaxScan — Frontend

Frontend SPA sederhana (HTML + CSS + ES Modules, tanpa library) untuk memeriksa
link artikel berita. Tidak ada login/register: halaman yang tersedia hanya
Home, Periksa link (Scan), Hasil, Riwayat, dan Tren.

## Struktur Folder

```
hoaxscan-frontend/
├── index.html            # Shell aplikasi, satu-satunya file HTML
├── css/
│   └── style.css         # Semua styling
└── js/
    ├── config.js         # Base URL backend + flag MOCK_MODE
    ├── api.js            # Satu pintu untuk semua request ke backend
    ├── mock.js           # Data contoh (dipakai saat MOCK_MODE = true)
    ├── router.js         # Navigasi antar "halaman" tanpa reload (hash router)
    ├── nav.js            # Menandai menu aktif & menutup menu mobile
    ├── app.js            # Titik masuk: mendaftarkan semua route
    └── pages/
        ├── home.js
        ├── scan.js       # Form periksa link
        ├── result.js     # Menampilkan hasil analisis
        ├── history.js    # Riwayat pemeriksaan
        └── trends.js     # Link yang sering diperiksa
```

## FE-01 vs FE-02: soal `MOCK_MODE`

Buka `js/config.js`:

- **`MOCK_MODE = true`** (kondisi saat ini, task FE-01): frontend jalan sendiri
  dengan data contoh dari `js/mock.js`. Hasil scan dibuat dari daftar domain
  tepercaya sederhana, riwayat disimpan di `localStorage`. Tidak butuh backend.
- **`MOCK_MODE = false`** (task FE-02): request dikirim ke `API_BASE_URL`
  lewat `api.js`.

Bentuk data sengaja sama antara mode mock dan mode asli
(`{ is_hoax, confidence_score, explanation, ... }`), jadi pindah ke FE-02 tidak
perlu menulis ulang halaman.

## Endpoint yang dipakai

| Method | Endpoint          | Keterangan                                   |
|--------|-------------------|-----------------------------------------------|
| POST   | `/submissions`    | Kirim `{ url }`, balikan hasil analisis       |
| GET    | `/scan/history/`  | Riwayat pemeriksaan (juga dipakai halaman Tren) |

Sesuaikan path dan nama field dengan backend tim. Kalau nama field respons
berbeda, ubah di `pages/result.js` dan `pages/history.js`.

## Menjalankan secara lokal

File JS memakai ES Modules, jadi **tidak bisa** dibuka lewat `file://`:

```bash
cd hoaxscan-frontend
python -m http.server 5500
```

lalu buka `http://localhost:5500`. Saat `MOCK_MODE = false`, pastikan backend
mengaktifkan CORS untuk alamat frontend.
