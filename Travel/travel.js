(() => {
  const messageText = "Use Shift + Scroll to scroll";
  let tooltip;

  const showTooltip = (el) => {
    if (tooltip) return;
    tooltip = document.createElement("div");
    tooltip.className = "scroll-tooltip";
    tooltip.textContent = messageText;
    document.body.appendChild(tooltip);

    const rect = el.getBoundingClientRect();
    tooltip.style.left = `${rect.left + rect.width / 2}px`;
    tooltip.style.top = `${rect.top - 10}px`;

    requestAnimationFrame(() => tooltip.classList.add("visible"));
  };

  const hideTooltip = () => {
    if (!tooltip) return;
    tooltip.classList.remove("visible");
    tooltip.addEventListener(
      "transitionend",
      () => {
        tooltip?.remove();
        tooltip = null;
      },
      { once: true }
    );
  };

  const initTooltip = () => {
    document.querySelectorAll(".photo-carousel img").forEach((img) => {
      img.addEventListener("mouseenter", () => showTooltip(img));
      img.addEventListener("mouseleave", hideTooltip);
    });
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initTooltip);
  } else {
    initTooltip();
  }
})();
