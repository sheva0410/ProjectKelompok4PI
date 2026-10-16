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

- **`MOCK_MODE = false`** (kondisi saat ini, FE-02): request dikirim ke
  `API_BASE_URL` (backend FastAPI, default `http://127.0.0.1:8000/api`).
- **`MOCK_MODE = true`** (FE-01): frontend jalan sendiri dengan data contoh
  dari `js/mock.js` dan riwayat di `localStorage`. Berguna untuk demo tanpa backend.

Halaman tidak memanggil `fetch()` langsung. Semuanya lewat tiga fungsi di
`api.js` (`submitUrl`, `getSubmission`, `listSubmissions`) yang mengubah respons
backend menjadi satu bentuk data untuk UI (`toUiResult`), sama untuk kedua mode.

## Endpoint yang dipakai

| Method | Endpoint                | Dipakai oleh                     |
|--------|-------------------------|----------------------------------|
| POST   | `/api/submissions`      | halaman Scan (kirim `{ url }`)   |
| GET    | `/api/submissions/{id}` | halaman Hasil (cek status ulang) |
| GET    | `/api/submissions`      | halaman Riwayat dan Tren         |

Pemetaan hasil backend ke UI: `label` `hoax` / `fakta` / `tidak_pasti` menjadi
"Terindikasi hoax" / "Cenderung kredibel" / "Tidak pasti"; `confidence` jadi
persen; `sources` jadi daftar rujukan. Submission tanpa `result` ditampilkan
sebagai "Belum dianalisis", dan halaman Hasil mengeceknya ulang tiap 3 detik
(maks. 10 kali).

## Menjalankan secara lokal

File JS memakai ES Modules, jadi **tidak bisa** dibuka lewat `file://`:

```bash
cd hoaxscan-frontend
python -m http.server 5500
```

lalu buka `http://localhost:5500`. Saat `MOCK_MODE = false`, tambahkan
`http://localhost:5500` ke `CORS_ORIGINS` di `.env` backend (bawaannya hanya
`http://localhost:5173`).
