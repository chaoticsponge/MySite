(function () {
  const run = () => {
    const el = document.getElementById('typed-name');
    if (!el) return;

    const text = el.dataset.text || el.textContent || '';
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (prefersReduced || !text.trim()) {
      el.textContent = text;
      return;
    }

    // Reserve space so layout stays stable before typing completes
    el.textContent = '';
    el.style.minHeight = getComputedStyle(el).lineHeight;
    const textNode = document.createTextNode('');
    const caret = document.createElement('span');
    caret.className = 'typed-caret';
    el.append(textNode, caret);
    const speed = 85;
    const pauseBetweenLines = 250;

    const lines = text.split(/\r?\n/);
    let lineIndex = 0;
    let charIndex = 0;

    const render = () => {
      const completed = lines.slice(0, lineIndex).join('\n');
      const currentLine = lines[lineIndex] || '';
      const typedCurrent = currentLine.slice(0, charIndex);
      const prefix = completed ? `${completed}\n` : '';
      textNode.nodeValue = `${prefix}${typedCurrent}`;
    };

    const step = () => {
      const currentLine = lines[lineIndex] || '';

      // Finished all lines
      if (lineIndex >= lines.length) return;

      // Typing current line
      if (charIndex < currentLine.length) {
        charIndex += 1;
        render();
        window.setTimeout(step, speed);
        return;
      }

      // Move to next line after a short pause
      lineIndex += 1;
      charIndex = 0;
      if (lineIndex < lines.length) {
        window.setTimeout(step, pauseBetweenLines);
      }
    };

    // Initial render to start typing
    render();
    window.setTimeout(step, speed);
  };

  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    run();
  } else {
    document.addEventListener('DOMContentLoaded', run);
  }
})();
