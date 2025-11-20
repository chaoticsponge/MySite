import os
from datetime import datetime
from pathlib import Path

BASE_URL = "https://emmr.me"
EXCLUDE_DIRS = {"error", "icons"}
BASE_DIR = Path(__file__).resolve().parent.parent
SITEMAP_PATH = BASE_DIR / "sitemap.xml"

def generate_sitemap():
    urls = []

    for root, _, files in os.walk(BASE_DIR):
        root_path = Path(root)
        rel_root = root_path.relative_to(BASE_DIR)
        rel_parts = [part for part in rel_root.parts if part not in (".", "")]

        # Skip hidden folders and excluded directories
        if any(part.startswith(".") for part in rel_parts):
            continue
        if any(part in EXCLUDE_DIRS for part in rel_parts):
            continue

        for file in files:
            if file.endswith(".html"):
                rel_path = (rel_root / file).as_posix()
                clean_url = rel_path.replace(".html", "")
                # Make sure URLs work with your .htaccess setup
                urls.append(f"{BASE_URL}/{clean_url}")

    # Write XML
    with open(SITEMAP_PATH, "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')

        for url in sorted(urls):
            f.write("  <url>\n")
            f.write(f"    <loc>{url}</loc>\n")
            f.write(f"    <lastmod>{datetime.utcnow().strftime('%Y-%m-%d')}</lastmod>\n")
            f.write("    <changefreq>monthly</changefreq>\n")
            f.write("    <priority>0.6</priority>\n")
            f.write("  </url>\n")

        f.write("</urlset>\n")

    print(f"✅ Sitemap generated with {len(urls)} URLs → {SITEMAP_PATH}")

if __name__ == "__main__":
    generate_sitemap()
