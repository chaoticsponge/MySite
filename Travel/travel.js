(() => {
  const bindHorizontalWheelScroll = (carousel) => {
    let velocity = 0;
    let rafId;

    const friction = 0.92; // lower = more glide
    const sensitivity = 0.55; // how much each wheel delta contributes
    const minVelocity = 0.05; // stop threshold
    const maxVelocity = 90; // cap to prevent jumps
    const blend = 0.25; // smooth out coarse mouse wheels

    const update = () => {
      if (Math.abs(velocity) < minVelocity) {
        velocity = 0;
        return;
      }

      carousel.scrollLeft += velocity;
      velocity *= friction;
      rafId = requestAnimationFrame(update);
    };

    const onWheel = (event) => {
      // Let true horizontal gestures (trackpad side scroll) behave normally.
      if (Math.abs(event.deltaX) > Math.abs(event.deltaY)) return;
      if (event.deltaY === 0) return;

      event.preventDefault();

      const isMouseWheel = Math.abs(event.deltaY) >= 50;
      const delta = event.deltaY * sensitivity;

      if (isMouseWheel) {
        velocity = velocity * (1 - blend) + delta * blend;
      } else {
        velocity += delta;
      }

      velocity = Math.max(-maxVelocity, Math.min(maxVelocity, velocity));

      cancelAnimationFrame(rafId);
      rafId = requestAnimationFrame(update);
    };

    carousel.addEventListener("wheel", onWheel, { passive: false });
  };

  const init = () => {
    document
      .querySelectorAll(".photo-carousel")
      .forEach(bindHorizontalWheelScroll);
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
