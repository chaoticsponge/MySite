(function () {
  const recentKey = "site-recent-pages";
  const email = "contact@emmr.me";
  const userAgent = navigator.userAgent || "";
  const reportedPlatform =
    navigator.userAgentData?.platform || navigator.platform || "";
  const hasAppleUserAgent = /Macintosh|Mac OS X|iPhone|iPad|iPod/i.test(
    userAgent,
  );
  const hasNonAppleUserAgent = /Windows|Android|Linux|CrOS|X11/i.test(
    userAgent,
  );
  const isApplePlatform = hasAppleUserAgent
    ? true
    : hasNonAppleUserAgent
      ? false
      : /Mac|iPhone|iPad|iPod/i.test(reportedPlatform);
  const shortcutLabel = isApplePlatform ? "⌘ K" : "Ctrl K";
  const baseItems = [
    {
      title: "Home",
      subtitle: "Navigation",
      url: "/",
      keywords: "home hmoe start landing main welcome",
    },
    {
      title: "About me",
      subtitle: "Navigation",
      url: "/aboutme",
      keywords:
        "about abotu profile bio biography cv curriculum vitae resume résumé experience career employment work history background education qualifications certifications certificates skills volunteering volunteer services contact hire hiring",
    },
    {
      title: "Blog",
      subtitle: "Navigation",
      url: "/blogpage",
      keywords:
        "blog blo articles article posts post writing guides guide tutorials tutorial learning educational research cybersecurity security tech technology blockchain travel",
    },
    {
      title: "Projects",
      subtitle: "Navigation",
      url: "/projects",
      keywords:
        "projects project projcts portfolio work code coding github software apps applications tools demos development builds repositories repos",
    },
    {
      title: "Photos",
      subtitle: "Navigation",
      url: "/photos",
      keywords:
        "photos photo phots photography pictures images gallery camera travel trips destinations places",
    },
    {
      title: "Movies",
      subtitle: "Navigation",
      url: "/movies/movies",
      keywords:
        "movies movie moives films film cinema watch watched diary letterboxd ratings",
    },
  ];
  let searchableItems = baseItems.slice();
  let visibleItems = [];
  let activeIndex = 0;
  let searchIndexPromise = null;

  function readRecent() {
    try {
      const stored = JSON.parse(localStorage.getItem(recentKey));
      return Array.isArray(stored) ? stored : [];
    } catch (error) {
      return [];
    }
  }

  function rememberPage() {
    if (window.location.origin === "null") return;
    const entry = {
      title: document.title || "Untitled page",
      url: window.location.pathname + window.location.search,
    };
    const recent = readRecent().filter(function (item) {
      return item.url !== entry.url;
    });
    try {
      localStorage.setItem(
        recentKey,
        JSON.stringify([entry].concat(recent).slice(0, 6)),
      );
    } catch (error) {}
  }

  function createPalette() {
    const dialog = document.createElement("dialog");
    dialog.className = "command-palette";
    dialog.setAttribute("aria-label", "Site command palette");
    dialog.innerHTML = `
      <div class="command-shell">
        <div class="command-input-row">
          <span class="command-prompt" aria-hidden="true">›</span>
          <input class="command-input" type="text" autocomplete="off" spellcheck="false" aria-label="Search or enter a command" placeholder="Search or type a command…">
          <kbd>Esc</kbd>
        </div>
        <div class="command-results" role="listbox" aria-label="Results"></div>
        <div class="command-footer">
          <span><kbd>↑</kbd><kbd>↓</kbd> navigate</span>
          <span><kbd>↵</kbd> open</span>
          <span class="command-footer-shortcut"><kbd>${isApplePlatform ? "⌘" : "Ctrl"}</kbd><kbd>K</kbd></span>
        </div>
      </div>`;
    document.body.appendChild(dialog);
    return dialog;
  }

  const dialog = createPalette();
  const input = dialog.querySelector(".command-input");
  const results = dialog.querySelector(".command-results");

  function createSidebarTrigger() {
    const sidebar = document.querySelector(".sidebar");
    const socialLinks = sidebar?.querySelector(".social-links");
    if (!sidebar || !socialLinks) return;

    const trigger = document.createElement("button");
    trigger.className = "command-trigger";
    trigger.type = "button";
    trigger.setAttribute(
      "aria-label",
      `Open site search and commands, ${shortcutLabel}`,
    );
    trigger.innerHTML = `<span>Search</span><kbd>${shortcutLabel}</kbd>`;
    trigger.addEventListener("click", openPalette);
    sidebar.classList.add("has-command-trigger");
    sidebar.insertBefore(trigger, socialLinks);
  }

  function normalize(value) {
    return (value || "")
      .toLocaleLowerCase()
      .normalize("NFKD")
      .replace(/\p{Diacritic}/gu, "")
      .replace(/[-_/]+/g, " ")
      .replace(/[^\p{L}\p{N}\s]/gu, "")
      .replace(/\s+/g, " ")
      .trim();
  }

  function queryTokens(value) {
    const ignoredWords = new Set([
      "a",
      "an",
      "the",
      "to",
      "for",
      "me",
      "please",
      "go",
      "open",
      "show",
      "find",
      "take",
      "switch",
      "set",
      "use",
      "page",
      "turn",
      "enable",
      "disable",
      "change",
      "make",
      "it",
      "my",
      "website",
      "site",
      "on",
    ]);
    return normalize(value)
      .split(/\s+/)
      .filter(function (token) {
        return token && !ignoredWords.has(token);
      });
  }

  function matchesQuery(value, query) {
    const haystack = normalize(value);
    const tokens = queryTokens(query);
    return (
      tokens.length > 0 &&
      tokens.every(function (token) {
        return haystack.includes(token);
      })
    );
  }

  function commandSignature(value) {
    return queryTokens(value).sort().join(" ");
  }

  function resolveCommand(value) {
    const normalized = normalize(value);
    if (commands[normalized]) return commands[normalized];
    const signature = commandSignature(value);
    const alias = Object.keys(commandAliases).find(function (name) {
      return commandSignature(name) === signature;
    });
    if (alias) return commands[commandAliases[alias]];
    const commandName = Object.keys(commands).find(function (name) {
      return commandSignature(name) === signature;
    });
    return commandName ? commands[commandName] : null;
  }

  function randomItem(items) {
    return items[Math.floor(Math.random() * items.length)];
  }

  function randomDestination() {
    const articles = searchableItems.filter(function (item) {
      return item.type === "Article";
    });
    const choices = ["article", "/projects", "/photos", "/movies/movies"];
    const choice = randomItem(choices);
    return choice === "article" && articles.length
      ? randomItem(articles).url
      : choice === "article"
        ? "/blogpage"
        : choice;
  }

  function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    try {
      localStorage.setItem("theme", theme);
    } catch (error) {}
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = theme === "dark" ? "#0f1115" : "#ffffff";
  }

  const commands = {
    home: function () {
      window.location.assign("/");
    },
    about: function () {
      window.location.assign("/aboutme");
    },
    blog: function () {
      window.location.assign("/blogpage");
    },
    projects: function () {
      window.location.assign("/projects");
    },
    photos: function () {
      window.location.assign("/photos");
    },
    movies: function () {
      window.location.assign("/movies/movies");
    },
    random: async function () {
      await ensureSearchIndex();
      window.location.assign(randomDestination());
    },
    surprise: async function () {
      await ensureSearchIndex();
      window.location.assign(randomDestination());
    },
    "theme dark": function () {
      applyTheme("dark");
      closePalette();
    },
    "theme light": function () {
      applyTheme("light");
      closePalette();
    },
    telegram: function () {
      window.open("https://t.me/spongier", "_blank", "noopener");
      closePalette();
    },
    linkedin: function () {
      window.open("https://linkedin.com/in/emmrod19", "_blank", "noopener");
      closePalette();
    },
    email: async function () {
      try {
        await navigator.clipboard.writeText(email);
        renderMessage("Email copied to clipboard", email);
      } catch (error) {
        window.location.href = `mailto:${email}`;
      }
    },
  };

  const commandAliases = {
    homepage: "home",
    hmoe: "home",
    "main page": "home",
    start: "home",
    "about me": "about",
    abotu: "about",
    profile: "about",
    bio: "about",
    cv: "about",
    resume: "about",
    experience: "about",
    blogs: "blog",
    blo: "blog",
    article: "blog",
    articles: "blog",
    post: "blog",
    posts: "blog",
    project: "projects",
    projcts: "projects",
    portfolio: "projects",
    github: "projects",
    photo: "photos",
    phots: "photos",
    gallery: "photos",
    pictures: "photos",
    movie: "movies",
    moives: "movies",
    film: "movies",
    films: "movies",
    cinema: "movies",
    letterboxd: "movies",
    "surprise me": "surprise",
    "random page": "random",
    "pick something": "random",
    lucky: "random",
    "dark theme": "theme dark",
    "dark mode": "theme dark",
    "mode dark": "theme dark",
    "night mode": "theme dark",
    "lights off": "theme dark",
    dark: "theme dark",
    drak: "theme dark",
    "light theme": "theme light",
    "light mode": "theme light",
    "mode light": "theme light",
    "day mode": "theme light",
    "lights on": "theme light",
    light: "theme light",
    ligth: "theme light",
    "e mail": "email",
    mail: "email",
    contact: "email",
    "contact email": "email",
    "copy email": "email",
    emial: "email",
    tg: "telegram",
    telegam: "telegram",
    "linked in": "linkedin",
    linkdin: "linkedin",
  };

  function aliasesFor(command) {
    return Object.keys(commandAliases)
      .filter(function (alias) {
        return commandAliases[alias] === command;
      })
      .join(" ");
  }

  function itemMatchesSignature(item, signature) {
    if (commandSignature(item.command) === signature) return true;
    return Object.keys(commandAliases).some(function (alias) {
      return (
        commandAliases[alias] === item.command &&
        commandSignature(alias) === signature
      );
    });
  }

  function commandItems() {
    return [
      { title: "random", subtitle: "Open a surprise page", command: "random" },
      {
        title: "theme dark",
        subtitle: "Switch to dark mode",
        command: "theme dark",
      },
      {
        title: "theme light",
        subtitle: "Switch to light mode",
        command: "theme light",
      },
      { title: "email", subtitle: "Copy contact email", command: "email" },
      { title: "telegram", subtitle: "Open Telegram", command: "telegram" },
      { title: "linkedin", subtitle: "Open LinkedIn", command: "linkedin" },
    ];
  }

  function renderMessage(title, subtitle) {
    visibleItems = [];
    results.innerHTML = `<div class="command-empty"><strong>${title}</strong><span>${subtitle}</span></div>`;
  }

  function resultButton(item, index) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "command-result";
    button.setAttribute("role", "option");
    button.dataset.index = String(index);
    button.innerHTML = `<span class="command-result-copy"><strong></strong><small></small></span><span class="command-result-type"></span>`;
    button.querySelector("strong").textContent = item.title;
    button.querySelector("small").textContent =
      item.subtitle || item.type || "Page";
    button.querySelector(".command-result-type").textContent = item.command
      ? "Command"
      : item.type || "Page";
    button.addEventListener("click", function () {
      runItem(item);
    });
    button.addEventListener("pointermove", function () {
      activeIndex = index;
      updateActive();
    });
    return button;
  }

  function updateActive() {
    const buttons = Array.from(results.querySelectorAll(".command-result"));
    buttons.forEach(function (button, index) {
      const active = index === activeIndex;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-selected", String(active));
    });
    buttons[activeIndex]?.scrollIntoView({ block: "nearest" });
  }

  function render() {
    const query = normalize(input.value);
    if (!query) {
      const recent = readRecent()
        .filter(function (item) {
          return item.url !== window.location.pathname + window.location.search;
        })
        .slice(0, 4)
        .map(function (item) {
          return { ...item, subtitle: "Recently visited", type: "Recent" };
        });
      visibleItems = recent.concat(commandItems().slice(0, 4));
    } else {
      const signature = commandSignature(query);
      const exactCommand = commandItems().filter(function (item) {
        return itemMatchesSignature(item, signature);
      });
      const matches = searchableItems.filter(function (item) {
        return matchesQuery(
          [item.title, item.subtitle, item.type, item.keywords].join(" "),
          query,
        );
      });
      const matchingCommands = commandItems().filter(function (item) {
        return (
          !itemMatchesSignature(item, signature) &&
          matchesQuery(
            `${item.title} ${item.subtitle} ${aliasesFor(item.command)}`,
            query,
          )
        );
      });
      visibleItems = exactCommand.concat(matches, matchingCommands).slice(0, 9);
    }

    results.replaceChildren();
    activeIndex = 0;
    if (!visibleItems.length) {
      renderMessage("No results", "Try a page name or command");
      return;
    }
    visibleItems.forEach(function (item, index) {
      results.appendChild(resultButton(item, index));
    });
    updateActive();
  }

  function runItem(item) {
    if (item.command && commands[item.command]) {
      commands[item.command]();
      return;
    }
    if (!item.url) return;
    if (
      /^https?:\/\//.test(item.url) &&
      !item.url.startsWith(window.location.origin)
    ) {
      window.open(item.url, "_blank", "noopener");
      closePalette();
    } else {
      window.location.assign(item.url);
    }
  }

  function openPalette() {
    if (!dialog.open) dialog.showModal();
    input.value = "";
    render();
    ensureSearchIndex();
    window.setTimeout(function () {
      input.focus();
    }, 0);
  }

  function closePalette() {
    if (dialog.open) dialog.close();
  }

  input.addEventListener("input", render);
  input.addEventListener("keydown", function (event) {
    if (event.key === "ArrowDown") {
      event.preventDefault();
      activeIndex = (activeIndex + 1) % Math.max(visibleItems.length, 1);
      updateActive();
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      activeIndex =
        (activeIndex - 1 + Math.max(visibleItems.length, 1)) %
        Math.max(visibleItems.length, 1);
      updateActive();
    } else if (event.key === "Enter") {
      event.preventDefault();
      const exact = resolveCommand(input.value);
      if (exact) exact();
      else if (visibleItems[activeIndex]) runItem(visibleItems[activeIndex]);
    }
  });

  dialog.addEventListener("click", function (event) {
    if (event.target === dialog) closePalette();
  });
  document.addEventListener("keydown", function (event) {
    if (
      (event.metaKey || event.ctrlKey) &&
      event.key.toLocaleLowerCase() === "k"
    ) {
      event.preventDefault();
      dialog.open ? closePalette() : openPalette();
    }
  });

  async function loadSearchIndex() {
    const requests = [
      fetch("/blogpage")
        .then(function (response) {
          return response.ok ? response.text() : "";
        })
        .then(function (html) {
          const page = new DOMParser().parseFromString(html, "text/html");
          return Array.from(page.querySelectorAll(".posts-list > li"))
            .map(function (post) {
              const link = post.querySelector(".post-link");
              return {
                title:
                  post.querySelector(".post-title")?.textContent.trim() ||
                  "Article",
                subtitle:
                  post.querySelector(".post-meta")?.textContent.trim() ||
                  "Article",
                type: link?.getAttribute("href")?.startsWith("/travel/")
                  ? "Travel"
                  : "Article",
                url: link?.getAttribute("href"),
                keywords: post.dataset.topics || "",
              };
            })
            .filter(function (item) {
              return item.url;
            });
        }),
      fetch("/projects")
        .then(function (response) {
          return response.ok ? response.text() : "";
        })
        .then(function (html) {
          const page = new DOMParser().parseFromString(html, "text/html");
          return Array.from(page.querySelectorAll(".project-card"))
            .map(function (card) {
              const link = card.querySelector(".project-card-link");
              return {
                title:
                  card.querySelector(".project-title")?.textContent.trim() ||
                  "Project",
                subtitle:
                  card.querySelector(".project-category")?.textContent.trim() ||
                  "Project",
                type: "Project",
                url: link?.getAttribute("href"),
                keywords:
                  card
                    .querySelector(".project-description")
                    ?.textContent.trim() || "",
              };
            })
            .filter(function (item) {
              return item.url;
            });
        }),
      fetch("/letterboxd/index.json")
        .then(function (response) {
          return response.ok ? response.json() : [];
        })
        .then(function (movies) {
          return movies.map(function (movie) {
            const url = new URL("/movies/movies", window.location.origin);
            url.searchParams.set("movie", movie.title);
            return {
              title: movie.title,
              subtitle: movie.release_year || "Movie",
              type: "Movie",
              url: url.pathname + url.search,
              keywords: "film letterboxd",
            };
          });
        }),
    ];
    const loaded = await Promise.allSettled(requests);
    loaded.forEach(function (result) {
      if (result.status === "fulfilled")
        searchableItems = searchableItems.concat(result.value);
    });
    if (dialog.open && input.value) render();
  }

  function ensureSearchIndex() {
    if (!searchIndexPromise) searchIndexPromise = loadSearchIndex();
    return searchIndexPromise;
  }

  rememberPage();
  createSidebarTrigger();
})();
