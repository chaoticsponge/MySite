(function () {
  let started = false;

  const run = () => {
    if (started) return;
    started = true;

    const el = document.getElementById("typed-name");
    if (!el) return;

    const text = el.dataset.text || el.textContent || "";
    const prefersReduced = window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    ).matches;

    if (prefersReduced || !text.trim()) {
      el.textContent = text;
      return;
    }

    el.textContent = "";
    const fallback = document.createElement("span");
    fallback.className = "typed-fallback";
    fallback.textContent = text;

    const live = document.createElement("span");
    live.className = "typed-live";

    const textNode = document.createTextNode("");
    const caret = document.createElement("span");
    caret.className = "typed-caret";
    live.append(textNode, caret);

    el.append(fallback, live);
    const speed = 85;
    const pauseBetweenLines = 250;

    const lines = text.split(/\r?\n/);
    let lineIndex = 0;
    let charIndex = 0;

    const render = () => {
      const completed = lines.slice(0, lineIndex).join("\n");
      const currentLine = lines[lineIndex] || "";
      const typedCurrent = currentLine.slice(0, charIndex);
      const prefix = completed ? `${completed}\n` : "";
      textNode.nodeValue = `${prefix}${typedCurrent}`;
    };

    const step = () => {
      const currentLine = lines[lineIndex] || "";

      if (lineIndex >= lines.length) return;

      if (charIndex < currentLine.length) {
        charIndex += 1;
        render();
        window.setTimeout(step, speed);
        return;
      }

      lineIndex += 1;
      charIndex = 0;
      if (lineIndex < lines.length) {
        window.setTimeout(step, pauseBetweenLines);
      }
    };

    render();
    window.setTimeout(step, speed);
  };

  const schedule = () => {
    if (window.requestIdleCallback) {
      requestIdleCallback(run, { timeout: 500 });
    } else {
      setTimeout(run, 0);
    }
  };

  if (
    document.readyState === "complete" ||
    document.readyState === "interactive"
  ) {
    schedule();
  } else {
    document.addEventListener("DOMContentLoaded", schedule);
  }
})();
