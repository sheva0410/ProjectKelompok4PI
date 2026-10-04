// router.js
// Router sederhana berbasis hash (#/scan, #/history, dst) supaya berpindah
// halaman tidak perlu reload dan tidak perlu backend khusus untuk routing.

const routes = {};
let rootEl;

export function registerRoute(path, renderFn) {
  routes[path] = renderFn;
}

export function initRouter(rootSelector) {
  rootEl = document.querySelector(rootSelector);
  window.addEventListener("hashchange", renderCurrentRoute);
  renderCurrentRoute();
}

function renderCurrentRoute() {
  const path = (window.location.hash || "#/").replace("#", "");
  const renderer = routes[path] || routes["/404"];

  rootEl.innerHTML = "";
  if (renderer) {
    renderer(rootEl);
  } else {
    rootEl.innerHTML = "<p>Halaman tidak ditemukan.</p>";
  }
}

export function navigate(path) {
  window.location.hash = path;
}
