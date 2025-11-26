(function () {
  var key = "theme";
  var root = document.documentElement;
  var btn = document.querySelector(".theme-toggle");
  var iconSun = btn ? btn.querySelector('[data-theme-icon="light"]') : null;
  var iconMoon = btn ? btn.querySelector('[data-theme-icon="dark"]') : null;

  var getPreferredTheme = function () {
    var stored = "";
    try {
      stored = localStorage.getItem(key);
    } catch (e) {}
    if (stored === "light" || stored === "dark") return stored;
    var prefersDark =
      window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches;
    return prefersDark ? "dark" : "light";
  };

  var applyTheme = function (theme) {
    root.dataset.theme = theme;
    try {
      localStorage.setItem(key, theme);
    } catch (e) {}
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) {
      meta.setAttribute("content", theme === "dark" ? "#0f1115" : "#ffffff");
    }
  };

  var toggleTheme = function () {
    var next = root.dataset.theme === "dark" ? "light" : "dark";
    applyTheme(next);
  };

  applyTheme(getPreferredTheme());
  if (btn) {
    btn.addEventListener("click", toggleTheme);
  }
})();
