import os
import re
from datetime import datetime

# -------------------------------
# CONFIG
# -------------------------------
BLOG_DIRS = ["Blog", "Travel"]
BLOG_PAGE = "blogpage.html"

ICON_IT = "https://api.iconify.design/tabler:device-laptop.svg?color=%23333333"
ICON_TRAVEL = "https://api.iconify.design/mdi:airplane.svg"
PIN_ICON = "https://api.iconify.design/pajamas:thumbtack-solid.svg?color=%23F8C471"

# -------------------------------
# HELPERS
# -------------------------------
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
def generate_post_entry(post_path, title, date_str, reading_time, is_travel=False):
    """Generate HTML list item for a post."""
    icon = ICON_TRAVEL if is_travel else ICON_IT
    meta = f"{date_str} · {reading_time}" if reading_time else date_str
    return f"""
  <li>
    <a href="{post_path}" class="post-link">
      <span class="post-heading">
        <img class="post-icon" src="{icon}" alt="Post icon" />
        <span class="post-title">{title}</span>
      </span>
      <span class="post-meta">{meta}</span>
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
    pinned_links = re.findall(r'href="([^"]+)"', "\n".join(pinned_matches))

    valid_pinned, removed_pinned = [], []
    for block in pinned_matches:
        link_match = re.search(r'href="([^"]+)"', block)
        if link_match:
            link = link_match.group(1)
            if os.path.exists(link):
                valid_pinned.append(block)
                print(f"[{link}] - pinned (kept)")
            else:
                removed_pinned.append(link)
                print(f"[{link}] - deleted (missing pinned post)")

    # -------------------------------
    # Preserve existing <span class="post-meta"> dates
    # -------------------------------
    existing_meta = dict(re.findall(
        r'href="([^"]+)".*?<span class="post-meta">(.*?)</span>',
        current_list, flags=re.DOTALL
    ))

    posts, added_posts, unchanged_posts = [], [], []
    all_current_posts = set(re.findall(r'href="([^"]+)"', current_list))

    for folder in BLOG_DIRS:
        if not os.path.exists(folder):
            continue
        for file in os.listdir(folder):
            if not file.endswith(".html") or "template" in file.lower():
                continue

            rel_path = f"{folder}/{file}"
            if rel_path in pinned_links:
                continue

            path = os.path.join(folder, file)
            title = extract_title(path)
            reading_time = estimate_reading_time(path)
            is_travel = "Travel" in folder

            # Preserve existing manually set date
            if rel_path in existing_meta:
                old_meta = existing_meta[rel_path]
                old_date_match = re.match(r"([A-Za-z]{3} \d{1,2}, \d{4})", old_meta.strip())
                if old_date_match:
                    date_str = old_date_match.group(1)
                else:
                    date_str = format_date(path)
            else:
                date_str = format_date(path)

            display_dt = parse_display_date(date_str, path)
            posts.append(
                (display_dt,
                 generate_post_entry(rel_path, title, date_str, reading_time, is_travel))
            )

            if rel_path in all_current_posts:
                unchanged_posts.append(rel_path)
                print(f"[{rel_path}] - unchanged")
            else:
                added_posts.append(rel_path)
                print(f"[{rel_path}] - added")

    # ✅ Sort non-pinned posts by creation date (newest first)
    posts.sort(key=lambda x: x[0], reverse=True)

    # Detect removed (deleted) posts
    removed_posts = [href for href in all_current_posts if not os.path.exists(href)]
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

# -------------------------------
if __name__ == "__main__":
    update_blogpage()
