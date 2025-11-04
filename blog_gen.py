import os
import re
from datetime import datetime

# Directories and files
ROOT_DIR = "."
BLOG_DIRS = ["Blog", "Travel"]  # Scan both
BLOG_PAGE = "blogpage.html"

# Icons
ICON_IT = "https://api.iconify.design/tabler:device-laptop.svg?color=%23333333"
ICON_TRAVEL = "https://api.iconify.design/mdi:airplane.svg"

def extract_title(file_path):
    """Extract <title> or <h1> text from the HTML post"""
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
    """Estimate reading time by word count (200 words/minute)"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            html = f.read()
        # Strip HTML tags
        text = re.sub(r"<[^>]+>", " ", html)
        words = len(re.findall(r"\b\w+\b", text))
        minutes = max(1, int(round(words / 60)))  # At least 1 min
        return f"{minutes} min read"
    except Exception:
        return ""

def format_date(path):
    """Return file creation date formatted for post-meta"""
    ts = os.path.getctime(path)
    dt = datetime.fromtimestamp(ts)
    return dt.strftime("%b %-d, %Y")

def generate_post_entry(post_path, title, date_str, reading_time, is_travel=False):
    """Generate one <li> entry"""
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

def update_blogpage():
    posts = []

    for folder in BLOG_DIRS:
        if not os.path.exists(folder):
            continue

        for file in os.listdir(folder):
            if not file.endswith(".html"):
                continue
            if "template" in file.lower() or file.startswith("."):
                continue  # Skip template or hidden files

            path = os.path.join(folder, file)
            title = extract_title(path)
            date_str = format_date(path)
            reading_time = estimate_reading_time(path)
            rel_path = f"{folder}/{file}"
            is_travel = "Travel" in folder
            posts.append(
                (os.path.getctime(path),
                 generate_post_entry(rel_path, title, date_str, reading_time, is_travel))
            )

    # Sort by creation date (newest first)
    posts.sort(reverse=True)

    # Read blogpage.html
    with open(BLOG_PAGE, "r", encoding="utf-8") as f:
        content = f.read()

    # Generate new post list HTML
    new_posts_html = "\n\n".join(p[1] for p in posts)

    # Replace content between <ul class="posts-list"> and </ul>
    updated = re.sub(
        r"(<ul class=\"posts-list\">)(.*?)(</ul>)",
        f"\\1\n{new_posts_html}\n\\3",
        content,
        flags=re.DOTALL,
    )

    with open(BLOG_PAGE, "w", encoding="utf-8") as f:
        f.write(updated)

    print(f"✅ Blog page updated with {len(posts)} posts (newest first).")

if __name__ == "__main__":
    update_blogpage()
