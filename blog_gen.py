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
PIN_ICON = "https://api.iconify.design/tabler:pin.svg?color=%23333333"

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
    """Estimate reading time based on word count (200 wpm)."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            html = f.read()
        text = re.sub(r"<[^>]+>", " ", html)
        words = len(re.findall(r"\b\w+\b", text))
        minutes = max(1, int(round(words / 200)))
        return f"{minutes} min read"
    except Exception:
        return ""

def format_date(path):
    """Use file creation date for display."""
    ts = os.path.getctime(path)
    dt = datetime.fromtimestamp(ts)
    return dt.strftime("%b %-d, %Y")

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
    # Load blog page
    with open(BLOG_PAGE, "r", encoding="utf-8") as f:
        content = f.read()

    # Match only the post list section, not sidebar nav
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

    valid_pinned = []
    removed_pinned = []

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
    # Build new post list
    # -------------------------------
    posts = []
    all_current_posts = set(re.findall(r'href="([^"]+)"', current_list))
    added_posts = []
    unchanged_posts = []

    for folder in BLOG_DIRS:
        if not os.path.exists(folder):
            continue
        for file in os.listdir(folder):
            if not file.endswith(".html") or "template" in file.lower():
                continue

            rel_path = f"{folder}/{file}"
            if rel_path in pinned_links:
                continue  # skip pinned ones

            path = os.path.join(folder, file)
            title = extract_title(path)
            date_str = format_date(path)
            reading_time = estimate_reading_time(path)
            is_travel = "Travel" in folder

            posts.append(
                (os.path.getctime(path),
                 generate_post_entry(rel_path, title, date_str, reading_time, is_travel))
            )

            if rel_path in all_current_posts:
                unchanged_posts.append(rel_path)
                print(f"[{rel_path}] - unchanged")
            else:
                added_posts.append(rel_path)
                print(f"[{rel_path}] - added")

    posts.sort(reverse=True)

    # Detect removed (deleted) posts
    all_new_posts = set([p[1] for p in posts]) | set(pinned_links)
    removed_posts = [
        href for href in all_current_posts
        if not os.path.exists(href)
    ]
    for r in removed_posts:
        print(f"[{r}] - deleted")

    # -------------------------------
    # Rebuild and replace content
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
# RUN
# -------------------------------
if __name__ == "__main__":
    update_blogpage()
