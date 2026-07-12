(function () {
  const search = document.getElementById("blog-search");
  const posts = Array.from(document.querySelectorAll(".posts-list > li"));
  const chips = Array.from(document.querySelectorAll(".topic-chip"));
  const status = document.querySelector(".blog-filter-status");
  if (!search || !posts.length || !chips.length) return;

  const validTopics = new Set(chips.map(function (chip) { return chip.dataset.topic; }));
  let topic = "all";
  let timer = 0;

  function normalize(value) {
    return (value || "").trim().toLocaleLowerCase();
  }

  function updateUrl(mode) {
    const url = new URL(window.location.href);
    const query = search.value.trim();
    if (topic === "all") url.searchParams.delete("topic");
    else url.searchParams.set("topic", topic);
    if (query) url.searchParams.set("q", query);
    else url.searchParams.delete("q");
    window.history[mode + "State"]({}, "", url);
  }

  function render() {
    const query = normalize(search.value);
    let visible = 0;

    posts.forEach(function (post) {
      const topics = (post.dataset.topics || "").split(/\s+/);
      const matchesTopic = topic === "all" || topics.includes(topic);
      const matchesSearch = !query || normalize(post.textContent).includes(query);
      const matches = matchesTopic && matchesSearch;
      post.hidden = !matches;
      if (matches) visible += 1;
    });

    chips.forEach(function (chip) {
      const selected = chip.dataset.topic === topic;
      chip.classList.toggle("is-active", selected);
      chip.setAttribute("aria-pressed", String(selected));
    });

    status.textContent = visible === 0
      ? "No articles match those filters."
      : visible === posts.length
        ? `${visible} articles`
        : `${visible} of ${posts.length} articles`;
    status.classList.toggle("is-empty", visible === 0);
  }

  function readUrl() {
    const params = new URLSearchParams(window.location.search);
    const requestedTopic = normalize(params.get("topic"));
    topic = validTopics.has(requestedTopic) ? requestedTopic : "all";
    search.value = params.get("q") || "";
    render();
  }

  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      topic = chip.dataset.topic;
      render();
      updateUrl("push");
    });
  });

  search.addEventListener("input", function () {
    render();
    window.clearTimeout(timer);
    timer = window.setTimeout(function () { updateUrl("replace"); }, 180);
  });

  window.addEventListener("popstate", readUrl);
  readUrl();
})();
