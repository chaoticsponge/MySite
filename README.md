# MySite

## Upload commands:

```
python3 /scripts/blog_gen.py
python3 /scripts/sitemap_gen.py
git add . etc.
flyctl deploy --remote-only
```

## Assets directory

- All CSS lives under `assets/`
- When adding new stylesheets, drop them in `assets/` and reference them with relative paths from root.
- If you relocate or rename a stylesheet, run `rg -n "old-name.css"` to update every `link` tag so pages don’t keep pointing at stale paths.
- https://icones.js.org/ rounded material

## File naming

- HTML files follow lowercase, dash-separated slugs (e.g. `travel/dj-singapore-template.html`, `blog/tryhackme-guide.html`) to avoid spaces/casing issues in URLs.
- When creating a new page, stick to this format and keep it under the appropriate section folder (`blog/`, `travel/`, etc.).
- If an existing page must be renamed, update the filename plus every internal link (run `rg -n "old-name"`), and double-check `sitemap.xml` so search engines get the new path.

# Adding Photos Pipeline:

1. gen alt text
2. Crop to square
3. ImgOptim

## Article publishing checklist

Use this before uploading a new article:

- [ ] Save the file with a lowercase, dash-separated name in the correct folder:
  - `blog/` for cybersecurity and general tech
  - `educational/` for explainers, including blockchain
  - `travel/` for travel posts
- [ ] Add a unique `<title>` and matching page `<h1>`.
- [ ] Add a concise `<meta name="description">` describing the article.
- [ ] Add `<meta name="author" content="Emmanuel Rodriguez">`.
- [ ] Set the clean canonical URL, without `.html`, in `<link rel="canonical">`.
- [ ] Add Open Graph metadata: `og:type`, `og:title`, `og:description`, `og:url`, and `og:site_name`.
- [ ] Add Twitter metadata: `twitter:card`, `twitter:title`, and `twitter:description`.
- [ ] Add or update the Article JSON-LD fields: `headline`, `description`, `url`, `author`, `datePublished`, `dateModified`, and `mainEntityOfPage`.
- [ ] Give every meaningful image descriptive `alt` text and use an empty `alt=""` only for decorative images.
- [ ] Check that internal links use clean root-relative URLs, for example `/blog/my-article`.
- [ ] Run `python3 scripts/blog_gen.py` to add the article to the blog page, calculate reading time, add breadcrumbs/byline information, and infer filter topics.
- [ ] Confirm the generated article has the expected filter topics on `blogpage.html`.
- [ ] Run `python3 scripts/sitemap_gen.py` and confirm the clean article URL appears in `sitemap.xml`.
- [ ] Preview locally with `python3 scripts/dev_server.py` and check desktop, mobile, light mode, and dark mode.

### Blog filter topics

The supported filter topics are `cybersecurity`, `tech`, `blockchain`, `educational`, and `travel`. `blog_gen.py` infers them from the article folder, filename, and title. If a new article is categorized incorrectly, update `infer_topics()` in `scripts/blog_gen.py`; do not only edit `data-topics` in `blogpage.html`, because the next generator run will rebuild that list.

## Local testing

- Clean URLs like `/blog/shodan-beginner-guide` will not work over `file://`.
- Run the local dev server instead:
  `python3 scripts/dev_server.py`
- Then open:
  `http://127.0.0.1:8000`

## Fly.io

Legacy files for fly.io have not been removed e.g. Dockerfile for preservation. Not required for github/cloudflare pages.
