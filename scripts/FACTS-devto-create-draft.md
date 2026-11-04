# Locked facts: scripts/devto_create_draft.py (2026-11-04)

## Goal
Add one Python 3 script that creates a **Dev.to draft** (`published: false`) from an existing `devto/**/*.yml` meta file plus its LinkedIn `source` markdown. Example meta:
`devto/physical-ai/2026-11-03-so101-sponge-paper-real-robot-walls.yml`

## Existing code (reuse, do not rewrite)
- `scripts/devto_payload.py` already builds the JSON payload (title, published, tags, canonical_url, series, body_markdown) with cover-strip + raw GitHub image rewrite. It refuses `published: true` and does not call the API.
- New script must import/reuse that payload logic (import functions or call `main`-equivalent helpers). Prefer importing `parse_simple_yaml`, `strip_leading_cover`, `absolutize_images`, `REQUIRED`, `PAYLOAD_KEYS`, `REPO_ROOT` from `devto_payload` rather than duplicating YAML/body transforms. If import of private helpers is awkward, factor shared helpers into `devto_payload.py` carefully without changing its CLI behavior.

## API (Forem / Dev.to v1)
- POST `https://dev.to/api/articles`
- Headers:
  - `api-key: <from env DEVTO_API_KEY>`
  - `Accept: application/vnd.forem.api-v1+json`
  - `Content-Type: application/json`
  - `User-Agent: yohei1126-writing-devto-create-draft/1.0` (or similar fixed string; required in practice)
- Body shape: `{"article": { ...payload fields... }}`
- Force `article.published` to `false` even if meta were wrong (also refuse if meta `published` is not false).
- Auth: only `DEVTO_API_KEY` env var. Never hardcode a key. Exit non-zero if missing.
- Stdlib only (`urllib.request` / `json`). No PyPI deps, no PyYAML.
- On success: print a short summary to stdout (id, url or path if present, title, published=false). Print API error body on failure.
- Do not PUT/update existing articles in v1 of this script. Create only.
- Do not set `main_image` / cover unless meta already has an absolute URL field (current PAI yml leaves cover unset — leave unset).
- tags: pass as list if API accepts list; Dev.to often wants comma string — use whatever matches current Forem docs for create (list of up to 4 is commonly accepted in JSON; if unsure, join with comma as string). Prefer list of strings matching payload tags when the API sample uses array; if docs show string, join with ", ".

## CLI
```
python3 scripts/devto_create_draft.py <devto-meta.yml>
```
- Path may be relative to cwd or absolute; resolve source paths via repo root like `devto_payload.py`.
- `--dry-run` optional: print the wrapped `{"article":...}` JSON and do not POST.

## Hard constraints
- Never create with `published: true`.
- Do not call the API in dry-run.
- Do not store API responses into the yml file.
- Do not edit LinkedIn articles or the example yml contents (read-only for those).
- Keep code style close to `devto_payload.py` (type hints, short docstring, clear errors).

## Out of scope
- No README/AGENTS rewrite unless a one-line pointer is necessary next to the script docstring.
- No git commit.
