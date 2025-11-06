const MOVIE_DIR = '/letterboxd/movies/';

async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Failed to fetch ${url}`);
  return res.json();
}

async function loadMovieMarkdown(filename) {
  try {
    const res = await fetch(`${MOVIE_DIR}${filename}`);
    const text = await res.text();
    const frontMatter = /^---\n([\s\S]*?)\n---/.exec(text);
    if (!frontMatter) return {};
    const yaml = Object.fromEntries(
      frontMatter[1]
        .split('\n')
        .filter(Boolean)
        .map(line => {
          const [key, ...rest] = line.split(':');
          return [key.trim(), rest.join(':').trim().replace(/^'|'$/g, '')];
        })
    );
    return yaml;
  } catch {
    return {};
  }
}

async function renderMovies() {
  const grid = document.getElementById('movie-grid');
  const index = await fetchJSON('/letterboxd/index.json');
  const movies = await Promise.all(
    index.map(async entry => {
      const m = await loadMovieMarkdown(entry.filename);
      return { ...entry, ...m };
    })
  );

  grid.innerHTML = movies
    .map(
      m => `
      <div class="movie-card">
        <img src="${m.cover_image}" alt="${m.display_title || m.title}">
        <div class="movie-info">
          <h3>${m.display_title || m.title} (${m.release_year || ''})</h3>
          <p>${m.watched_date ? new Date(m.watched_date).toLocaleDateString() : ''}</p>
        </div>
      </div>
    `
    )
    .join('');
}

document.addEventListener('DOMContentLoaded', renderMovies);
