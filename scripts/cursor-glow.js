(function () {
  const glow = document.querySelector(".cursor-glow");
  if (!glow) return;

  const canHover = window.matchMedia("(hover: hover) and (pointer: fine)");
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  let frame = 0;
  let x = -500;
  let y = -500;

  function render() {
    glow.style.transform = `translate3d(${x}px, ${y}px, 0) translate(-50%, -50%)`;
    frame = 0;
  }

  function handlePointer(event) {
    if (!canHover.matches || reducedMotion.matches) return;
    x = event.clientX;
    y = event.clientY;
    glow.classList.add("is-visible");
    if (!frame) frame = window.requestAnimationFrame(render);
  }

  function hide() {
    glow.classList.remove("is-visible");
  }

  window.addEventListener("pointermove", handlePointer, { passive: true });
  document.documentElement.addEventListener("mouseleave", hide);
  window.addEventListener("blur", hide);
})();
