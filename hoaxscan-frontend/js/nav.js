// nav.js
// Menutup menu navigasi mobile dan menandai halaman yang sedang aktif.

export function updateNavbar() {
  const navLinks = document.getElementById("nav-links");
  const navToggle = document.getElementById("nav-toggle");
  navLinks?.classList.remove("open");
  navToggle?.setAttribute("aria-expanded", "false");

  const route = (window.location.hash || "#/").replace("#", "");
  document.querySelectorAll(".nav-links a").forEach((link) => {
    link.classList.toggle("active", link.getAttribute("href") === `#${route}`);
  });
}
