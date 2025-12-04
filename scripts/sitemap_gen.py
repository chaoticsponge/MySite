import os
from datetime import datetime, timezone
from pathlib import Path

BASE_URL = "https://emmr.me"
# Directories we never want in the sitemap (beyond dot-folders)
EXCLUDE_DIRS = {
    "error",      # error pages live under assets/error
    "assets",     # static assets
    "icons",
    "scripts",
    "favicon",
    "cron",
    "letterboxd", # tooling/exports not meant for indexing
    "node_modules",
}
# Specific HTML files to skip even if discovered
EXCLUDE_FILES = {"403.html", "404.html", "301.html"}
BASE_DIR = Path(__file__).resolve().parent.parent
SITEMAP_PATH = BASE_DIR / "sitemap.xml"

def generate_sitemap():
    urls = []

    for root, dirs, files in os.walk(BASE_DIR):
        root_path = Path(root)
        rel_root = root_path.relative_to(BASE_DIR)
        rel_parts = [part for part in rel_root.parts if part not in (".", "")]

        # Prune hidden and excluded directories from traversal
        dirs[:] = [
            d for d in dirs
            if not d.startswith(".") and d not in EXCLUDE_DIRS
        ]

        # Skip this root if any part is excluded (after pruning)
        if any(part.startswith(".") for part in rel_parts):
            continue
        if any(part in EXCLUDE_DIRS for part in rel_parts):
            continue

        for file in files:
            if file.endswith(".html"):
                if file in EXCLUDE_FILES:
                    continue

                rel_path = (rel_root / file).as_posix()
                clean_url = rel_path.replace(".html", "")
                if clean_url.endswith("/index"):
                    clean_url = clean_url[: -len("/index")]
                if clean_url == "index":
                    clean_url = ""

                # Make sure URLs work with your .htaccess setup
                urls.append(f"{BASE_URL}/{clean_url}")

    # Write XML
    with open(SITEMAP_PATH, "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')

        for url in sorted(urls):
            f.write("  <url>\n")
            f.write(f"    <loc>{url}</loc>\n")
            f.write(f"    <lastmod>{datetime.now(timezone.utc).strftime('%Y-%m-%d')}</lastmod>\n")
            f.write("    <changefreq>monthly</changefreq>\n")
            f.write("    <priority>0.6</priority>\n")
            f.write("  </url>\n")

        f.write("</urlset>\n")

    print(f"✅ Sitemap generated with {len(urls)} URLs → {SITEMAP_PATH}")

if __name__ == "__main__":
    generate_sitemap()
