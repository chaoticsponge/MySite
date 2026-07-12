(function () {
  if (!document.querySelector(".article-container > article")) return;

  const root = document.documentElement;
  const storageKey = "article-reader-preferences";
  const defaults = { size: "default", width: "default" };
  const allowed = {
    size: new Set(["small", "default", "large"]),
    width: new Set(["narrow", "default", "wide"])
  };

  function loadPreferences() {
    try {
      const saved = JSON.parse(localStorage.getItem(storageKey));
      return {
        size: allowed.size.has(saved && saved.size) ? saved.size : defaults.size,
        width: allowed.width.has(saved && saved.width) ? saved.width : defaults.width
      };
    } catch (error) {
      return { ...defaults };
    }
  }

  function savePreferences(preferences) {
    try {
      localStorage.setItem(storageKey, JSON.stringify(preferences));
    } catch (error) {}
  }

  const preferences = loadPreferences();
  const controls = document.createElement("div");
  controls.className = "reader-controls";
  controls.innerHTML = `
    <button class="reader-toggle" type="button" aria-expanded="false" aria-controls="reader-panel" aria-label="Reading preferences">Aa</button>
    <div class="reader-panel" id="reader-panel" hidden>
      <div class="reader-option-group" role="group" aria-labelledby="reader-size-label">
        <span class="reader-option-label" id="reader-size-label">Text size</span>
        <div class="reader-segments">
          <button type="button" data-reader-setting="size" data-reader-value="small">Small</button>
          <button type="button" data-reader-setting="size" data-reader-value="default">Default</button>
          <button type="button" data-reader-setting="size" data-reader-value="large">Large</button>
        </div>
      </div>
      <div class="reader-option-group" role="group" aria-labelledby="reader-width-label">
        <span class="reader-option-label" id="reader-width-label">Reading width</span>
        <div class="reader-segments">
          <button type="button" data-reader-setting="width" data-reader-value="narrow">Narrow</button>
          <button type="button" data-reader-setting="width" data-reader-value="default">Default</button>
          <button type="button" data-reader-setting="width" data-reader-value="wide">Wide</button>
        </div>
      </div>
      <button class="reader-reset" type="button">Reset to default</button>
    </div>`;
  document.body.appendChild(controls);

  const toggle = controls.querySelector(".reader-toggle");
  const panel = controls.querySelector(".reader-panel");
  const optionButtons = Array.from(controls.querySelectorAll("[data-reader-setting]"));
  const reset = controls.querySelector(".reader-reset");

  function applyPreferences() {
    root.dataset.readerSize = preferences.size;
    root.dataset.readerWidth = preferences.width;
    optionButtons.forEach(function (button) {
      const selected = preferences[button.dataset.readerSetting] === button.dataset.readerValue;
      button.classList.toggle("is-active", selected);
      button.setAttribute("aria-pressed", String(selected));
    });
  }

  function closePanel() {
    panel.hidden = true;
    toggle.setAttribute("aria-expanded", "false");
  }

  toggle.addEventListener("click", function () {
    const willOpen = panel.hidden;
    panel.hidden = !willOpen;
    toggle.setAttribute("aria-expanded", String(willOpen));
  });

  optionButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      preferences[button.dataset.readerSetting] = button.dataset.readerValue;
      applyPreferences();
      savePreferences(preferences);
    });
  });

  reset.addEventListener("click", function () {
    preferences.size = defaults.size;
    preferences.width = defaults.width;
    applyPreferences();
    savePreferences(preferences);
  });

  document.addEventListener("click", function (event) {
    if (!controls.contains(event.target)) closePanel();
  });
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && !panel.hidden) {
      closePanel();
      toggle.focus();
    }
  });

  applyPreferences();
})();
