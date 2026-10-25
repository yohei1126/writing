#!/usr/bin/env python3
"""Print a Dev.to article payload from registration metadata and LinkedIn markdown.

Reads a devto/*.yml meta file and the LinkedIn article at its `source` path.
Writes JSON to stdout: title, published, tags, canonical_url, series, body_markdown.

body_markdown is the LinkedIn file text unchanged. cover_note is not an API field.
This script does not call the Dev.to API. It refuses published: true.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ("title", "published", "tags", "canonical_url", "series", "source")
PAYLOAD_KEYS = ("title", "published", "tags", "canonical_url", "series")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(f"usage: {Path(argv[0]).name} <devto-meta.yml>", file=sys.stderr)
        return 2
    meta_path = Path(argv[1])
    if not meta_path.is_file():
        print(f"meta file not found: {meta_path}", file=sys.stderr)
        return 1
    meta = parse_simple_yaml(meta_path.read_text(encoding="utf-8"))
    missing = [key for key in REQUIRED if key not in meta]
    if missing:
        print(f"missing fields: {', '.join(missing)}", file=sys.stderr)
        return 1
    if meta["published"] is not False:
        print("published must be false; this script does not prepare a live post", file=sys.stderr)
        return 1
    if not isinstance(meta["tags"], list) or not meta["tags"]:
        print("tags must be a non-empty list", file=sys.stderr)
        return 1
    for key in ("title", "canonical_url", "series", "source"):
        if not isinstance(meta[key], str) or not meta[key].strip():
            print(f"{key} must be a non-empty string", file=sys.stderr)
            return 1
    source = REPO_ROOT / meta["source"]
    if not source.is_file():
        print(f"source article not found: {source}", file=sys.stderr)
        return 1
    payload = {key: meta[key] for key in PAYLOAD_KEYS}
    payload["body_markdown"] = source.read_text(encoding="utf-8")
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


def parse_simple_yaml(text: str) -> dict:
    """Parse the flat subset used by devto metadata files.

    Supports comments, double- or single-quoted scalars, true/false,
    flow lists, and one-level block lists. No nested maps.
    """
    data: dict = {}
    current_list: str | None = None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        line = raw.split(" #", 1)[0].rstrip()
        if line.startswith(("  - ", "- ")):
            if current_list is None:
                raise SystemExit(f"list item outside a key: {raw!r}")
            item = line.split("- ", 1)[1].strip()
            data[current_list].append(parse_scalar(item))
            continue
        if ":" not in line:
            raise SystemExit(f"expected key: value, got {raw!r}")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value == "":
            data[key] = []
            current_list = key
            continue
        current_list = None
        data[key] = parse_scalar(value)
    return data


def parse_scalar(value: str):
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    if value == "true":
        return True
    if value == "false":
        return False
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(part.strip()) for part in inner.split(",")]
    return value


if __name__ == "__main__":
    sys.exit(main(sys.argv))
