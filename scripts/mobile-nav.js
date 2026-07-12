(function () {
  const sidebar = document.querySelector(".sidebar");
  if (!sidebar) return;

  const mobile = window.matchMedia("(max-width: 860px), (hover: none) and (pointer: coarse) and (orientation: landscape) and (max-height: 500px)");
  const article = document.querySelector(".article-container > article");
  let lastY = Math.max(window.scrollY, 0);
  let ticking = false;

  function normalizePath(path) {
    const normalized = (path || "/").replace(/\/index\.html$/, "/").replace(/\.html$/, "");
    return normalized.length > 1 ? normalized.replace(/\/$/, "") : normalized;
  }

  function updateScrollState() {
    const y = Math.max(window.scrollY, 0);
    const delta = y - lastY;
    const maxScroll = Math.max(document.documentElement.scrollHeight - window.innerHeight, 1);
    const nearBottom = maxScroll - y < 60;

    if (!mobile.matches || y < 80 || nearBottom || delta < -8) {
      sidebar.classList.remove("is-nav-hidden");
    } else if (delta > 8) {
      sidebar.classList.add("is-nav-hidden");
    }

    if (article) {
      const progress = sidebar.querySelector(".mobile-reading-progress-fill");
      const value = sidebar.querySelector(".mobile-reading-progress");
      const percentage = Math.min(100, Math.max(0, (y / maxScroll) * 100));
      if (progress) progress.style.transform = `scaleX(${percentage / 100})`;
      if (value) value.setAttribute("aria-valuenow", String(Math.round(percentage)));
    }

    lastY = y;
    ticking = false;
  }

  function handleScroll() {
    if (!ticking) {
      ticking = true;
      window.requestAnimationFrame(updateScrollState);
    }
  }

  function createArticleNavigation() {
    const nav = document.createElement("div");
    nav.className = "mobile-reading-nav";
    nav.setAttribute("aria-label", "Article navigation");
    nav.innerHTML = `
      <a class="mobile-reading-link mobile-reading-prev" aria-label="Previous article">
        <img src="https://api.iconify.design/material-symbols:chevron-left-rounded.svg" alt="" aria-hidden="true">
      </a>
      <a class="mobile-reading-center" href="/blogpage" aria-label="Back to all articles">
        <span class="mobile-reading-label">Reading progress</span>
        <span class="mobile-reading-progress" role="progressbar" aria-label="Article reading progress" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0">
          <span class="mobile-reading-progress-fill"></span>
        </span>
      </a>
      <a class="mobile-reading-link mobile-reading-next" aria-label="Next article">
        <img src="https://api.iconify.design/material-symbols:chevron-right-rounded.svg" alt="" aria-hidden="true">
      </a>`;
    sidebar.appendChild(nav);
    sidebar.classList.add("has-reading-nav");

    fetch("/blogpage")
      .then(function (response) {
        if (!response.ok) throw new Error("Unable to load article index");
        return response.text();
      })
      .then(function (html) {
        const documentCopy = new DOMParser().parseFromString(html, "text/html");
        const posts = Array.from(documentCopy.querySelectorAll(".posts-list .post-link"));
        const current = normalizePath(window.location.pathname);
        const index = posts.findIndex(function (link) {
          return normalizePath(new URL(link.href, window.location.origin).pathname) === current;
        });
        if (index < 0) return;

        const previous = posts[index - 1];
        const next = posts[index + 1];
        const previousLink = nav.querySelector(".mobile-reading-prev");
        const nextLink = nav.querySelector(".mobile-reading-next");

        if (previous) {
          previousLink.href = previous.getAttribute("href");
          previousLink.title = previous.querySelector(".post-title")?.textContent.trim() || "Previous article";
        } else {
          previousLink.setAttribute("aria-disabled", "true");
        }
        if (next) {
          nextLink.href = next.getAttribute("href");
          nextLink.title = next.querySelector(".post-title")?.textContent.trim() || "Next article";
        } else {
          nextLink.setAttribute("aria-disabled", "true");
        }
      })
      .catch(function () {
        nav.querySelectorAll(".mobile-reading-link").forEach(function (link) {
          link.setAttribute("aria-disabled", "true");
        });
      });
  }

  if (article) createArticleNavigation();
  window.addEventListener("scroll", handleScroll, { passive: true });
  mobile.addEventListener("change", function () {
    sidebar.classList.remove("is-nav-hidden");
    updateScrollState();
  });
  updateScrollState();
})();
