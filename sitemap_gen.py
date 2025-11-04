import os
from datetime import datetime

BASE_URL = "https://emmr.me"
EXCLUDE_DIRS = {"error", "icons"}
SITEMAP_PATH = "sitemap.xml"

def generate_sitemap():
    urls = []

    for root, _, files in os.walk("."):
        # Skip hidden folders and excluded directories
        if any(excl in root for excl in EXCLUDE_DIRS) or root.startswith("./."):
            continue

        for file in files:
            if file.endswith(".html"):
                path = os.path.join(root, file).replace("./", "")
                clean_url = path.replace(".html", "")
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
