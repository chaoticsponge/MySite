#!/usr/bin/env python3
from __future__ import annotations

import argparse
import posixpath
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent.parent


def resolve_clean_path(request_path: str) -> Path | None:
    parsed = urlsplit(request_path)
    clean_path = unquote(parsed.path)

    if clean_path in ("", "/"):
        return ROOT / "index.html"

    relative = clean_path.lstrip("/")
    direct = ROOT / relative
    if direct.is_file():
        return direct

    if not Path(relative).suffix:
        html_candidate = ROOT / f"{relative}.html"
        if html_candidate.is_file():
            return html_candidate

        index_candidate = ROOT / relative / "index.html"
        if index_candidate.is_file():
            return index_candidate

    return None


class CleanURLHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def translate_path(self, path: str) -> str:
        resolved = resolve_clean_path(path)
        if resolved is not None:
            return str(resolved)

        path = urlsplit(path).path
        path = posixpath.normpath(unquote(path))
        words = [word for word in path.split("/") if word]
        translated = ROOT
        for word in words:
            translated = translated / word
        return str(translated)

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Serve the site locally with extensionless URL support."
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to. Default: 8000",
    )
    args = parser.parse_args()

    server = ThreadingHTTPServer(("127.0.0.1", args.port), CleanURLHandler)
    print(f"Serving {ROOT} at http://127.0.0.1:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
