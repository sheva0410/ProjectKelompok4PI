// empty.js
// Tampilan "masih kosong" untuk halaman yang belum punya data (Riwayat, Tren).

const ICONS = {
  // Lembar arsip dengan kaca pembesar
  riwayat: `<svg viewBox="0 0 64 64" aria-hidden="true"><rect x="12" y="8" width="32" height="42" rx="3" fill="var(--surface)" stroke="currentColor" stroke-width="3"/><path d="M19 19h18M19 27h18M19 35h10" stroke="currentColor" stroke-width="3" stroke-linecap="round"/><circle cx="44" cy="42" r="9" fill="var(--yellow)" stroke="currentColor" stroke-width="3"/><path d="M50.5 48.5 57 55" stroke="currentColor" stroke-width="4" stroke-linecap="round"/></svg>`,
  // Diagram batang dengan panah naik
  tren: `<svg viewBox="0 0 64 64" aria-hidden="true"><path d="M10 54h46" stroke="currentColor" stroke-width="3" stroke-linecap="round"/><rect x="14" y="36" width="9" height="18" rx="2" fill="var(--mint)" stroke="currentColor" stroke-width="3"/><rect x="28" y="26" width="9" height="28" rx="2" fill="var(--blue)" stroke="currentColor" stroke-width="3"/><rect x="42" y="16" width="9" height="38" rx="2" fill="var(--pink)" stroke="currentColor" stroke-width="3"/><path d="M12 24 26 12l8 6 14-10" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
};

export function renderEmpty({ icon, title, text, actionHref = "#/scan", actionLabel = "Periksa link" }) {
  return `
    <div class="empty-state">
      <span class="empty-icon">${ICONS[icon] || ""}</span>
      <h3>${title}</h3>
      <p>${text}</p>
      <a class="button button-primary" href="${actionHref}">${actionLabel}</a>
    </div>`;
}
