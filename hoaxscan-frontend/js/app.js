// app.js
// Titik masuk aplikasi. Tugasnya cuma satu: mendaftarkan setiap route
// ke fungsi render halaman yang sesuai, lalu menyalakan router.

import { initRouter, registerRoute } from "./router.js";
import { updateNavbar } from "./nav.js";
import { renderHome } from "./pages/home.js";
import { renderScan } from "./pages/scan.js";
import { renderResult } from "./pages/result.js";
import { renderHistory } from "./pages/history.js";
import { renderTrends } from "./pages/trends.js";

registerRoute("/", renderHome);
registerRoute("/scan", renderScan);
registerRoute("/result", renderResult);
registerRoute("/history", renderHistory);
registerRoute("/trends", renderTrends);
registerRoute("/404", (root) => {
  root.innerHTML = "<h2>404 - Halaman tidak ditemukan</h2>";
});

window.addEventListener("hashchange", updateNavbar);
updateNavbar();
initRouter("#app");
