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

## File naming

- HTML files follow lowercase, dash-separated slugs (e.g. `travel/dj-singapore-template.html`, `blog/tryhackme-guide.html`) to avoid spaces/casing issues in URLs.
- When creating a new page, stick to this format and keep it under the appropriate section folder (`blog/`, `travel/`, etc.).
- If an existing page must be renamed, update the filename plus every internal link (run `rg -n "old-name"`), and double-check `sitemap.xml` so search engines get the new path.

# Adding Photos Pipeline:

1. gen alt text
2. Crop to square
3. ImgOptim

# Tagging posts

Learning tag:
<img class="post-icon" src="https://api.iconify.design/tabler:pencil.svg?color=%23fb8c00" alt="Learning icon" />

## Local testing

- Clean URLs like `/blog/shodan-beginner-guide` will not work over `file://`.
- Run the local dev server instead:
  `python3 scripts/dev_server.py`
- Then open:
  `http://127.0.0.1:8000`
