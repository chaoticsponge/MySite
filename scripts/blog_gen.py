import os
import re
from datetime import datetime
from html import unescape
from pathlib import Path

# -------------------------------
# CONFIG
# -------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
BLOG_PAGE = BASE_DIR / "blogpage.html"

ICON_IT = "https://api.iconify.design/tabler:device-laptop.svg?color=%23406B38"
ICON_TRAVEL = "https://api.iconify.design/mdi:airplane.svg?color=%235DADE2"
ICON_LEARNING = "https://api.iconify.design/tabler:pencil.svg?color=%23fb8c00"
PIN_ICON = "https://api.iconify.design/pajamas:thumbtack-solid.svg?color=%23F8C471"

BLOG_SOURCES = [
    {"path": BASE_DIR / "blog", "icon": ICON_IT},
    {"path": BASE_DIR / "travel", "icon": ICON_TRAVEL},
    {"path": BASE_DIR / "educational", "icon": ICON_LEARNING},
]

DEFAULT_AUTHOR = "Emmanuel Rodriguez"
SECTION_LABELS = {
    "blog": "Tech",
    "travel": "Travel",
    "educational": "Educational",
}

# -------------------------------
# HELPERS
# -------------------------------
def normalize_href(href):
    """Normalize href for comparisons (case-insensitive, no leading ./)."""
    return href.strip().lstrip("./").replace("\\", "/").lower()


def extract_title(file_path):
    """Extract <title> or <h1> from HTML file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            html = f.read()
        match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE)
        if not match:
            match = re.search(r"<h1.*?>(.*?)</h1>", html, re.IGNORECASE)
        return match.group(1).strip() if match else os.path.basename(file_path)
    except Exception:
        return os.path.basename(file_path)


def strip_html(text):
    """Remove tags and normalize entities/whitespace."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def extract_h1(html):
    """Extract the first visible h1."""
    match = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.IGNORECASE | re.DOTALL)
    return strip_html(match.group(1)) if match else ""


def format_long_date(iso_date):
    """Convert YYYY-MM-DD to 'Month D, YYYY'."""
    try:
        return datetime.strptime(iso_date, "%Y-%m-%d").strftime("%B %-d, %Y")
    except ValueError:
        return iso_date


def format_short_date(iso_date):
    """Convert YYYY-MM-DD to 'Mon D, YYYY'."""
    try:
        return datetime.strptime(iso_date, "%Y-%m-%d").strftime("%b %-d, %Y")
    except ValueError:
        return iso_date


def parse_iso_date(iso_date):
    """Parse YYYY-MM-DD safely for comparisons."""
    try:
        return datetime.strptime(iso_date, "%Y-%m-%d")
    except ValueError:
        return None


def extract_schema_value(html, key):
    """Extract a simple JSON-LD string value like datePublished or author name."""
    match = re.search(rf'"{re.escape(key)}"\s*:\s*"([^"]+)"', html)
    return match.group(1).strip() if match else ""


def extract_author_name(html):
    """Extract author name from JSON-LD, falling back to the site default."""
    author_block = re.search(
        r'"author"\s*:\s*\{{.*?"name"\s*:\s*"([^"]+)"',
        html,
        re.IGNORECASE | re.DOTALL,
    )
    if author_block:
        return author_block.group(1).strip()
    return DEFAULT_AUTHOR


def build_breadcrumb_html(path):
    """Build a consistent breadcrumb trail based on folder."""
    section_key = path.parent.name
    section_label = SECTION_LABELS.get(section_key, section_key.title())
    return (
        '        <nav class="article-breadcrumbs" aria-label="Breadcrumb">\n'
        '          <a href="/index.html">Home</a>\n'
        '          <span aria-hidden="true">/</span>\n'
        '          <a href="/blogpage.html">Blog</a>\n'
        '          <span aria-hidden="true">/</span>\n'
        f'          <span>{section_label}</span>\n'
        '        </nav>'
    )


def build_article_meta_html(author, published, modified):
    """Build the visible byline/date line from schema dates."""
    published_label = format_long_date(published) if published else ""
    modified_label = format_long_date(modified) if modified else ""

    parts = [f"By {author}"]
    if published_label:
        parts.append(f"Published {published_label}")
    if modified_label:
        parts.append(f"Updated {modified_label}")

    return f'        <p class="article-meta">{" • ".join(parts)}</p>'


def sync_schema_modified_date(html, modified_iso):
    """Write dateModified back into JSON-LD when present."""
    if not modified_iso or not re.search(r'"dateModified"\s*:\s*"[^"]+"', html):
        return html
    return re.sub(
        r'("dateModified"\s*:\s*")[^"]+(")',
        lambda match: f'{match.group(1)}{modified_iso}{match.group(2)}',
        html,
        count=1,
    )


def extract_article_dates(path):
    """Read schema dates from an article file, with filesystem fallback for publish date."""
    html = path.read_text(encoding="utf-8")
    published = extract_schema_value(html, "datePublished")
    modified = extract_schema_value(html, "dateModified")
    if not published:
      published = datetime.fromtimestamp(os.path.getctime(path)).strftime("%Y-%m-%d")
    return published, modified


def update_article_page(path):
    """Ensure article pages include breadcrumb and visible author/date metadata."""
    html = path.read_text(encoding="utf-8")
    original = html

    breadcrumb_html = build_breadcrumb_html(path)

    if re.search(r'<nav class="article-breadcrumbs" aria-label="Breadcrumb">.*?</nav>', html, re.DOTALL):
        html = re.sub(
            r'<nav class="article-breadcrumbs" aria-label="Breadcrumb">.*?</nav>',
            breadcrumb_html,
            html,
            count=1,
            flags=re.DOTALL,
        )
    else:
        html = re.sub(
            r"(<article>\s*)",
            r"\1" + breadcrumb_html + "\n\n",
            html,
            count=1,
        )

    author = extract_author_name(html)
    published = extract_schema_value(html, "datePublished")
    modified = extract_schema_value(html, "dateModified")
    if not published:
        published = datetime.fromtimestamp(os.path.getctime(path)).strftime("%Y-%m-%d")
    published_dt = parse_iso_date(published)
    modified_dt = parse_iso_date(modified)
    if published_dt and modified_dt and modified_dt < published_dt:
        modified = published
        html = sync_schema_modified_date(html, modified)
    article_meta_html = build_article_meta_html(author, published, modified)

    if re.search(r'<p class="article-meta">.*?</p>', html, re.DOTALL):
        html = re.sub(
            r'<p class="article-meta">.*?</p>',
            article_meta_html,
            html,
            count=1,
            flags=re.DOTALL,
        )
    else:
        html = re.sub(
            r"(<h1[^>]*>.*?</h1>\s*)",
            r"\1" + article_meta_html + "\n\n",
            html,
            count=1,
            flags=re.DOTALL,
        )

    if html != original:
        path.write_text(html, encoding="utf-8")
        print(f"[{path.relative_to(BASE_DIR).as_posix()}] - article metadata updated")
    else:
        print(f"[{path.relative_to(BASE_DIR).as_posix()}] - article metadata unchanged")

def estimate_reading_time(file_path):
    """Estimate reading time based on word count (60 wpm)."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            html = f.read()
        text = re.sub(r"<[^>]+>", " ", html)
        words = len(re.findall(r"\b\w+\b", text))
        minutes = max(1, int(round(words / 60)))
        return f"{minutes} min read"
    except Exception:
        return ""

def format_date(path):
    """Use file creation date for display."""
    ts = os.path.getctime(path)
    dt = datetime.fromtimestamp(ts)
    return dt.strftime("%b %-d, %Y")

def parse_display_date(date_str, fallback_path):
    """Convert displayed date (e.g., 'Jan 3, 2024') into a datetime for sorting."""
    cleaned = date_str.strip()
    match = re.match(r"([A-Za-z]{3})\s+(\d{1,2}),\s*(\d{4})", cleaned)
    if match:
        month, day, year = match.groups()
        try:
            normalized = f"{month} {int(day):02d} {year}"
            return datetime.strptime(normalized, "%b %d %Y")
        except ValueError:
            pass
    # Fallback to filesystem modification time if parsing fails
    return datetime.fromtimestamp(os.path.getmtime(fallback_path))
def generate_post_entry(post_path, title, date_str, reading_time, icon):
    """Generate HTML list item for a post with the provided icon."""
    meta = f"{date_str} · {reading_time}" if reading_time else date_str
    return f"""
  <li>
    <a href="{post_path}" class="post-link">
      <img class="post-icon" src="{icon}" alt="Post icon" />
      <span class="post-copy">
        <span class="post-title">{title}</span>
        <span class="post-meta">{meta}</span>
      </span>
    </a>
  </li>
""".strip()

# -------------------------------
# MAIN UPDATE FUNCTION
# -------------------------------
def update_blogpage():
    with open(BLOG_PAGE, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r'(<ul class="posts-list">)(.*?)(</ul>)'
    match = re.search(pattern, content, flags=re.DOTALL)
    if not match:
        print("❌ Could not find <ul class=\"posts-list\"> in blogpage.html")
        return

    current_list = match.group(2)

    # -------------------------------
    # Detect pinned posts
    # -------------------------------
    pinned_matches = re.findall(
        r'(<li>.*?' + re.escape(PIN_ICON) + r'.*?</li>)', current_list, flags=re.DOTALL
    )
    pinned_links_raw = re.findall(r'href="([^"]+)"', "\n".join(pinned_matches))
    pinned_links = {normalize_href(link) for link in pinned_links_raw}

    valid_pinned, removed_pinned = [], []
    for block in pinned_matches:
        link_match = re.search(r'href="([^"]+)"', block)
        if link_match:
            link = link_match.group(1)
            if (BASE_DIR / link).exists():
                valid_pinned.append(block)
                print(f"[{link}] - pinned (kept)")
            else:
                removed_pinned.append(link)
                print(f"[{link}] - deleted (missing pinned post)")

    posts, added_posts, unchanged_posts = [], [], []
    all_current_posts_raw = re.findall(r'href="([^"]+)"', current_list)
    all_current_posts = {normalize_href(href) for href in all_current_posts_raw}

    for source in BLOG_SOURCES:
        folder = source["path"]
        icon = source["icon"]

        if not folder.exists():
            continue
        for file in os.listdir(folder):
            if not file.endswith(".html") or "template" in file.lower():
                continue

            path = folder / file
            rel_path = path.relative_to(BASE_DIR).as_posix()
            normalized_rel_path = normalize_href(rel_path)

            if normalized_rel_path in pinned_links:
                continue

            title = extract_title(path)
            reading_time = estimate_reading_time(path)
            published, _ = extract_article_dates(path)
            date_str = format_short_date(published) if published else format_date(path)

            display_dt = parse_display_date(date_str, path)
            posts.append(
                (display_dt,
                 generate_post_entry(rel_path, title, date_str, reading_time, icon))
            )

            if normalized_rel_path in all_current_posts:
                unchanged_posts.append(rel_path)
                print(f"[{rel_path}] - unchanged")
            else:
                added_posts.append(rel_path)
                print(f"[{rel_path}] - added")

    # ✅ Sort non-pinned posts by creation date (newest first)
    posts.sort(key=lambda x: x[0], reverse=True)

    # Detect removed (deleted) posts
    removed_posts = [href for href in all_current_posts_raw if not (BASE_DIR / href).exists()]
    for r in removed_posts:
        print(f"[{r}] - deleted")

    # -------------------------------
    # Rebuild HTML
    # -------------------------------
    new_posts_html = ""
    if valid_pinned:
        new_posts_html += "\n".join(valid_pinned) + "\n\n<!-- --- Pinned Above --- -->\n\n"
    new_posts_html += "\n\n".join(p[1] for p in posts)

    updated = re.sub(pattern, f"\\1\n{new_posts_html}\n\\3", content, flags=re.DOTALL)

    with open(BLOG_PAGE, "w", encoding="utf-8") as f:
        f.write(updated)

    # -------------------------------
    # Summary
    # -------------------------------
    print("\n--- SUMMARY ---")
    print(f"Updated: {BLOG_PAGE}")
    print(f"{len(valid_pinned)} pinned kept")
    print(f"{len(added_posts)} added")
    print(f"{len(unchanged_posts)} unchanged")
    print(f"{len(removed_posts) + len(removed_pinned)} removed")


def update_article_pages():
    """Normalize breadcrumb and visible article metadata across article folders."""
    for source in BLOG_SOURCES:
        folder = source["path"]
        if not folder.exists():
            continue
        for file in sorted(os.listdir(folder)):
            if not file.endswith(".html") or "template" in file.lower():
                continue
            update_article_page(folder / file)

# -------------------------------
if __name__ == "__main__":
    update_article_pages()
    update_blogpage()
