#!/usr/bin/env python3
import json
from pathlib import Path
import yaml
from datetime import datetime

MOVIE_DIR = Path(__file__).parent / "movies"
INDEX_PATH = "index.json"

def to_iso(value):
    """Convert datetime/date to ISO string if needed."""
    if isinstance(value, (datetime,)):
        return value.isoformat()
    return value

def build_index():
    MOVIE_DIR.mkdir(exist_ok=True)
    entries = []

    for file in MOVIE_DIR.rglob("*.md"):
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()

        parts = []
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    data = yaml.safe_load(parts[1]) or {}
                except Exception:
                    data = {}
            else:
                data = {}
        else:
            data = {}

        raw_front_matter = parts[1] if len(parts) >= 3 else ""

        cover_image = data.get("cover_image")
        needs_normalization = False
        normalized_cover_image = cover_image

        if isinstance(cover_image, str):
            normalized_cover_image = cover_image.strip()
            if "\n" in normalized_cover_image:
                normalized_cover_image = "".join(
                    part.strip() for part in normalized_cover_image.splitlines()
                )
            if normalized_cover_image != cover_image:
                needs_normalization = True

        if "cover_image: >" in raw_front_matter and normalized_cover_image:
            needs_normalization = True

        if needs_normalization and normalized_cover_image and len(parts) >= 3:
            data["cover_image"] = normalized_cover_image

            front_dump = yaml.safe_dump(
                data,
                sort_keys=False,
                width=1000,
                default_flow_style=False,
            ).strip()

            remainder = parts[2]
            new_content = f"---\n{front_dump}\n---{remainder}"
            file.write_text(new_content, encoding="utf-8")

        entry = {
            "filename": str(file.relative_to(MOVIE_DIR)),
            "title": data.get("display_title") or data.get("title"),
            "release_year": data.get("release_year"),
            "cover_image": data.get("cover_image"),
            "watched_date": to_iso(data.get("watched_date")),
            "date_added": to_iso(data.get("date")),
            "rewatch": data.get("rewatch", False),
        }

        entries.append(entry)

    # Sort newest watched_date first if available
    def sort_key(e):
        return e.get("watched_date") or e.get("date_added") or ""
    entries.sort(key=sort_key, reverse=True)

    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)

    print(f"Indexed {len(entries)} movies → {INDEX_PATH}")

if __name__ == "__main__":
    build_index()
