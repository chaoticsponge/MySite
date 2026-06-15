import os
import json
from datetime import datetime, timezone
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

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


class PageMetadataParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonical = None
        self.modified_time = None
        self.noindex = False
        self._in_json_ld = False
        self._json_ld_parts = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)

        if tag == "link" and "canonical" in attributes.get("rel", "").split():
            self.canonical = attributes.get("href")

        if (
            tag == "meta"
            and attributes.get("property") == "article:modified_time"
        ):
            self.modified_time = attributes.get("content")

        if tag == "meta" and attributes.get("name", "").lower() == "robots":
            directives = attributes.get("content", "").lower().split(",")
            self.noindex = any(item.strip() == "noindex" for item in directives)

        if tag == "script" and attributes.get("type") == "application/ld+json":
            self._in_json_ld = True
            self._json_ld_parts = []

    def handle_data(self, data):
        if self._in_json_ld:
            self._json_ld_parts.append(data)

    def handle_endtag(self, tag):
        if tag != "script" or not self._in_json_ld:
            return

        self._in_json_ld = False
        try:
            structured_data = json.loads("".join(self._json_ld_parts))
        except json.JSONDecodeError:
            return

        if not self.modified_time:
            self.modified_time = find_date_modified(structured_data)


def find_date_modified(value):
    if isinstance(value, dict):
        if value.get("dateModified"):
            return value["dateModified"]
        for child in value.values():
            result = find_date_modified(child)
            if result:
                return result
    elif isinstance(value, list):
        for child in value:
            result = find_date_modified(child)
            if result:
                return result
    return None


def fallback_url(file_path):
    rel_path = file_path.relative_to(BASE_DIR)
    clean_path = rel_path.with_suffix("").as_posix()
    if clean_path.endswith("/index"):
        clean_path = clean_path[: -len("/index")]
    if clean_path == "index":
        clean_path = ""
    return f"{BASE_URL}/{clean_path}"


def page_metadata(file_path):
    parser = PageMetadataParser()
    parser.feed(file_path.read_text(encoding="utf-8"))

    if parser.noindex:
        return None

    url = parser.canonical or fallback_url(file_path)
    parsed_url = urlparse(url)
    if parsed_url.scheme not in {"http", "https"} or parsed_url.netloc != "emmr.me":
        raise ValueError(f"Invalid canonical URL in {file_path}: {url}")

    if parser.modified_time:
        last_modified = parser.modified_time[:10]
    else:
        modified_timestamp = file_path.stat().st_mtime
        last_modified = datetime.fromtimestamp(
            modified_timestamp, timezone.utc
        ).strftime("%Y-%m-%d")

    return url, last_modified


def generate_sitemap():
    pages = {}

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

                file_path = root_path / file
                metadata = page_metadata(file_path)
                if metadata is None:
                    continue

                url, last_modified = metadata
                if url in pages:
                    raise ValueError(f"Duplicate canonical URL: {url}")
                pages[url] = last_modified

    # Write XML
    with open(SITEMAP_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')

        for url, last_modified in sorted(pages.items()):
            f.write("  <url>\n")
            f.write(f"    <loc>{escape(url)}</loc>\n")
            f.write(f"    <lastmod>{last_modified}</lastmod>\n")
            f.write("    <changefreq>monthly</changefreq>\n")
            f.write("    <priority>0.6</priority>\n")
            f.write("  </url>\n")

        f.write("</urlset>\n")

    print(f"Sitemap generated with {len(pages)} URLs -> {SITEMAP_PATH}")

if __name__ == "__main__":
    generate_sitemap()
