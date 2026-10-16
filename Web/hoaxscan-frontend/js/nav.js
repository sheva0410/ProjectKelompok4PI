// nav.js
// Navbar: menandai halaman aktif, menutup menu mobile, tombol tema, dan tautan "Lewati ke isi".

export function updateNavbar() {
  const navLinks = document.getElementById("nav-links");
  const navToggle = document.getElementById("nav-toggle");
  navLinks?.classList.remove("open");
  navToggle?.setAttribute("aria-expanded", "false");

  const route = (window.location.hash || "#/").replace("#", "");
  document.querySelectorAll(".nav-links a").forEach((link) => {
    const active = link.getAttribute("href") === `#${route}`;
    link.classList.toggle("active", active);
    if (active) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  });
}

// --- Tema: otomatis (ikut sistem) -> gelap -> terang ------------------------
const THEME_KEY = "hoaxscan_theme";
const THEMES = ["auto", "dark", "light"];
const THEME_TEXT = { auto: "Otomatis", dark: "Gelap", light: "Terang" };

function readTheme() {
  try {
    const t = localStorage.getItem(THEME_KEY);
    return THEMES.includes(t) ? t : "auto";
  } catch {
    return "auto";
  }
}

function applyTheme(theme) {
  const root = document.documentElement;
  if (theme === "auto") delete root.dataset.theme;
  else root.dataset.theme = theme;

  const dark = theme === "dark" || (theme === "auto" && window.matchMedia("(prefers-color-scheme: dark)").matches);
  document.getElementById("theme-color")?.setAttribute("content", dark ? "#121514" : "#ffffff");

  const btn = document.getElementById("theme-toggle");
  if (btn) {
    btn.querySelector(".theme-text").textContent = THEME_TEXT[theme];
    btn.setAttribute("aria-label", `Tema: ${THEME_TEXT[theme].toLowerCase()}. Klik untuk mengganti.`);
  }
}

export function initTheme() {
  let theme = readTheme();
  applyTheme(theme);
  document.getElementById("theme-toggle")?.addEventListener("click", () => {
    theme = THEMES[(THEMES.indexOf(theme) + 1) % THEMES.length];
    try {
      if (theme === "auto") localStorage.removeItem(THEME_KEY);
      else localStorage.setItem(THEME_KEY, theme);
    } catch {
      // tanpa penyimpanan, tema hanya berlaku sampai halaman ditutup
    }
    applyTheme(theme);
  });
  // Mode otomatis ikut berubah kalau pengaturan sistem berubah.
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => {
    if (theme === "auto") applyTheme(theme);
  });
}

// --- "Lewati ke isi": langsung ke konten tanpa mengubah alamat (#/...) -------
export function initSkipLink() {
  document.getElementById("skip-link")?.addEventListener("click", (e) => {
    e.preventDefault();
    document.getElementById("app")?.focus();
  });
}
