#!/usr/bin/env python3
"""Create a Dev.to draft (published: false) from a devto/*.yml meta file.

Usage: python3 scripts/devto_create_draft.py [--dry-run] <devto-meta.yml>

Payload building reuses helpers from devto_payload.py. Auth is read only from
the DEVTO_API_KEY environment variable. Create only: no update, no publish.
--dry-run prints the wrapped {"article": ...} JSON and makes no network call.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

from devto_payload import (
    PAYLOAD_KEYS,
    REPO_ROOT,
    REQUIRED,
    absolutize_images,
    parse_simple_yaml,
    strip_leading_cover,
)

API_URL = "https://dev.to/api/articles"
USER_AGENT = "yohei1126-writing-devto-create-draft/1.0"


def build_article(meta_path: Path) -> dict:
    """Validate meta and build the article payload (published forced false)."""
    meta = parse_simple_yaml(meta_path.read_text(encoding="utf-8"))
    missing = [key for key in REQUIRED if key not in meta]
    if missing:
        raise SystemExit(f"missing fields: {', '.join(missing)}")
    if meta["published"] is not False:
        raise SystemExit("published must be false; this script only creates drafts")
    tags = meta["tags"]
    if not isinstance(tags, list) or not tags or not all(isinstance(t, str) for t in tags):
        raise SystemExit("tags must be a non-empty list of strings")
    for key in ("title", "canonical_url", "series", "source"):
        if not isinstance(meta[key], str) or not meta[key].strip():
            raise SystemExit(f"{key} must be a non-empty string")
    source = REPO_ROOT / meta["source"]
    if not source.is_file():
        raise SystemExit(f"source article not found: {source}")
    article = {key: meta[key] for key in PAYLOAD_KEYS}
    body = strip_leading_cover(source.read_text(encoding="utf-8"))
    article["body_markdown"] = absolutize_images(body)
    article["published"] = False
    return article


def post_draft(article: dict, api_key: str) -> dict:
    """POST the article to Dev.to and return the parsed JSON response."""
    data = json.dumps({"article": article}, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        API_URL,
        data=data,
        method="POST",
        headers={
            "api-key": api_key,
            "Accept": "application/vnd.forem.api-v1+json",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Dev.to API error {err.code}: {body}")
    except urllib.error.URLError as err:
        raise SystemExit(f"request failed: {err.reason}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Create a Dev.to draft from a meta yml.")
    parser.add_argument("meta", help="path to devto meta yml")
    parser.add_argument("--dry-run", action="store_true", help="print payload, do not POST")
    args = parser.parse_args(argv[1:])

    meta_path = Path(args.meta)
    if not meta_path.is_file():
        print(f"meta file not found: {meta_path}", file=sys.stderr)
        return 1
    article = build_article(meta_path)

    if args.dry_run:
        json.dump({"article": article}, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0

    api_key = os.environ.get("DEVTO_API_KEY", "").strip()
    if not api_key:
        print("DEVTO_API_KEY is not set", file=sys.stderr)
        return 1
    result = post_draft(article, api_key)
    print(f"id: {result.get('id')}")
    print(f"url: {result.get('url') or result.get('path')}")
    print(f"title: {result.get('title', article['title'])}")
    print("published: false")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
