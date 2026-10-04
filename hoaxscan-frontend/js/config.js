// Alamat API FastAPI HoaxScan diatur dari satu tempat ini.
// Saat backend sudah di-deploy, cukup ganti nilai ini saja.
export const API_BASE_URL = "http://127.0.0.1:8000/api";

// === FE-01 vs FE-02 ===
// MOCK_MODE = true  -> frontend jalan sendiri pakai data contoh (localStorage),
//                      TIDAK butuh backend menyala. Ini yang dipakai untuk FE-01.
// MOCK_MODE = false -> request dikirim ke backend di API_BASE_URL.
export const MOCK_MODE = true;
