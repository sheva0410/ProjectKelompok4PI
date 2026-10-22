// tilt.js
// Efek 3D: elemen bertanda data-tilt miring halus mengikuti kursor.
// Nilai data-tilt = sudut maksimum dalam derajat (bawaan 8).
// Hanya aktif di perangkat bermouse dan kalau pengguna tidak memilih "kurangi gerakan".

const canTilt = () =>
  window.matchMedia("(hover: hover) and (pointer: fine)").matches &&
  !window.matchMedia("(prefers-reduced-motion: reduce)").matches;

export function enableTilt(root) {
  if (!canTilt()) return;
  root.querySelectorAll("[data-tilt]").forEach((el) => {
    const max = Number(el.dataset.tilt) || 8;
    let frame = 0;

    el.addEventListener("pointermove", (e) => {
      if (e.pointerType !== "mouse") return;
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        const r = el.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width - 0.5;
        const y = (e.clientY - r.top) / r.height - 0.5;
        el.classList.add("is-tilting");
        el.classList.remove("is-settling");
        el.style.setProperty("--ry", `${(x * max * 2).toFixed(2)}deg`);
        el.style.setProperty("--rx", `${(-y * max * 2).toFixed(2)}deg`);
      });
    });

    el.addEventListener("pointerleave", () => {
      cancelAnimationFrame(frame);
      el.classList.remove("is-tilting");
      el.classList.add("is-settling");
      // Kembali ke pose diam bawaan dari CSS (bisa datar, bisa sedikit miring).
      el.style.removeProperty("--rx");
      el.style.removeProperty("--ry");
    });
  });
}
