# AGENTS.md

Agent-oriented index for this repository. Read before editing outreach drafts here.

## Purpose

Markdown sources for **non-Zenn** outreach writing by Yohei (LinkedIn articles/posts now; X posts, talk drafts, etc. later).

- **Zenn** Japanese articles and season plans: [yohei1126/zenn](https://github.com/yohei1126/zenn) — do not move Zenn content here.
- **This repo** holds English (and other) outreach drafts that are published manually outside Zenn.

## Directory map

| Path | Commit | Description |
| :--- | :---: | :--- |
| `linkedin/` | yes | LinkedIn article and feed-post Markdown (flat or series subfolders) |
| `linkedin/ontographia/` | yes | Ontographia English series (Parts 1–3 article/post pairs) |
| `devto/` | yes | Dev.to registration metadata only (not article bodies) |
| `devto/ontographia/` | yes | Ontographia Dev.to meta (`published: false`) |
| `scripts/devto_payload.py` | yes | Build a Dev.to payload JSON from LinkedIn markdown + `devto/` meta. Does not call the API. |
| `README.md` | yes | Human-oriented overview |
| `.markdownlint.json` | yes | markdownlint rules (long lines allowed) |

## LinkedIn file conventions

### Flat drafts

```text
linkedin/YYYY-MM-DD-slug-{article|post}.en.md
```

### Multi-part series

Series drafts live under `linkedin/<series>/`. Filenames keep date + slug + `{article|post}.en.md`, and put the series name and `partN` in the slug so Parts 1, 2, 3 are obvious at a glance:

```text
linkedin/<series>/YYYY-MM-DD-<series>-partN-<topic-slug>-{article|post}.en.md
```

| Suffix | Role |
| :--- | :--- |
| `-article.en.md` | Long-form LinkedIn article body |
| `-post.en.md` | Feed post draft (often paired with the same-date article) |

### Ontographia series (finalized)

Folder: `linkedin/ontographia/`

| Part | Article | Post |
| :--- | :--- | :--- |
| 1 | `2026-09-08-ontographia-part1-template-cost-article.en.md` | `…-part1-template-cost-post.en.md` |
| 2 | `2026-09-08-ontographia-part2-intent-first-design-article.en.md` | `…-part2-intent-first-design-post.en.md` |
| 3 | `2026-09-08-ontographia-part3-eval-and-roadmap-article.en.md` | `…-part3-eval-and-roadmap-post.en.md` |

Do not leave Ontographia drafts as flat files under `linkedin/`. Keep Part number, topic slug, and the `article` / `post` suffix aligned for each pair.

Rules when working here:

- Prefer **English** for LinkedIn drafts unless the user asks otherwise.
- **Do not rewrite existing article/post body** unless the user explicitly requests an edit; treat migrated files as source of truth.
- Do not add Zenn front matter (`title`, `emoji`, `type`, `topics`, etc.) to LinkedIn files.
- Publishing is **manual** (copy into LinkedIn UI). Agents draft and revise Markdown only; they do not post.
- Keep paired article/post filenames aligned (same date + slug, different `{article|post}` suffix) when creating a new pair.
- LinkedIn paste constraints: Markdown only; no tables, HTML, or Mermaid in article/post bodies intended for paste.

### Ontographia article audience and depth

For Ontographia LinkedIn **article** bodies (Parts 1–3):

- Write so a non-engineer can follow the problem, the approach, and the results in plain language.
- Prefer mechanism and trade-offs over code. Do not embed long code samples, Cypher/JSON walkthroughs, or CLI dumps in the article body.
- When implementers need depth, point to a concrete public docs URL or repository path (for example the [architecture guide](https://edgesentry.github.io/ontographia/architecture/), [Evaluation guide](https://edgesentry.github.io/ontographia/evaluation/), or `examples/llm/eval/`).
- Keep existing verified numbers and claims; do not invent metrics or round claims up.

## Dev.to metadata

The LinkedIn article Markdown is the canonical body. `devto/` holds registration metadata only. Do not copy the article prose into `devto/`.

```text
devto/<series>/YYYY-MM-DD-<series>-partN-<topic-slug>.yml
```

Fields: `title`, `published` (keep `false`), `tags`, `canonical_url`, `series`, `source` (repo path of the LinkedIn article). Optional `cover_note` (not sent to the API).

`scripts/devto_payload.py` reads one meta file and prints JSON (`title`, `published`, `tags`, `canonical_url`, `series`, `body_markdown`). `body_markdown` is the LinkedIn file unchanged. The script does not call the Dev.to API. After merge, a separate step registers the draft with `published: false`.

## Writing skills (required before review)

Refine wording with the appropriate skill **before** asking for review. Do not skip this for new or substantially edited drafts.

| Language | Skill | Purpose / source |
| :--- | :--- | :--- |
| Japanese | `japanese-tech-writing` | Japanese technical prose. Source: https://gist.github.com/k16shikano/fd287c3133457c4fd8f5601d34aa817d |
| English | `english-tech-blog-structure` | Article structure for tech posts. Source: https://github.com/yohei1126/agent-skills/tree/main/english-tech-blog-structure (adapted from getsentry/skills blog-writing-guide: https://github.com/getsentry/skills/blob/main/skills/blog-writing-guide/SKILL.md) |
| English | `humanizer` | Remove sentence-level AI-writing tells. Source: https://github.com/blader/humanizer |

For English LinkedIn articles/posts, apply **`english-tech-blog-structure` first, then `humanizer`**, before review. Keep facts and numbers; do not invent claims. Path-only moves or link fixes do not require a prose pass.

## Lint before push

Run markdownlint locally before pushing:

```bash
npm install
npm run lint
```

Config is `.markdownlint.json` (based on yohei1126/zenn; line length and LinkedIn-prose-friendly rules are relaxed). CI runs the same check via `.github/workflows/markdownlint.yml`. Fix every CI failure before handoff; do not leave CI red for review.

## External repos

| URL | Role |
| :--- | :--- |
| [yohei1126/zenn](https://github.com/yohei1126/zenn) | Zenn series manuscripts (`articles/`) and planning (`instructions/`) |
| [edgesentry/ontographia](https://github.com/edgesentry/ontographia) | Open-source project referenced by the Ontographia LinkedIn drafts |

## Success criteria for edits

- Filenames match the convention above (series folder + `partN` when applicable).
- Wording refined with the skills above before review (when prose changed).
- `npm run lint` / CI markdownlint passes.
- LinkedIn drafts remain English Markdown suitable for manual paste/publish.
- `devto/` stays metadata. Article prose is not duplicated there.
- No Zenn-only tooling or season-plan workflow is assumed here.
