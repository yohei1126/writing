# AGENTS.md

Agent-oriented index for this repository. Read before editing outreach drafts here.

## Purpose

Markdown sources for **non-Zenn** outreach writing by Yohei (LinkedIn articles/posts now; X posts, talk drafts, etc. later).

- **Zenn** Japanese articles and season plans: [yohei1126/zenn](https://github.com/yohei1126/zenn) — do not move Zenn content here.
- **This repo** holds English (and other) outreach drafts that are published manually outside Zenn.

## Directory map

| Path | Commit | Description |
| :--- | :---: | :--- |
| `linkedin/` | yes | LinkedIn article and feed-post Markdown |
| `README.md` | yes | Human-oriented overview |
| `.markdownlint.json` | yes | markdownlint rules (long lines allowed) |

## LinkedIn file conventions

Naming:

```text
linkedin/YYYY-MM-DD-slug-{article|post}.en.md
```

| Suffix | Role |
| :--- | :--- |
| `-article.en.md` | Long-form LinkedIn article body |
| `-post.en.md` | Feed post draft (often paired with the same-date article) |

Rules when working here:

- Prefer **English** for LinkedIn drafts unless the user asks otherwise.
- **Do not rewrite existing article/post body** unless the user explicitly requests an edit; treat migrated files as source of truth.
- Do not add Zenn front matter (`title`, `emoji`, `type`, `topics`, etc.) to LinkedIn files.
- Publishing is **manual** (copy into LinkedIn UI). Agents draft and revise Markdown only; they do not post.
- Keep paired article/post filenames aligned (same date + slug, different `{article|post}` suffix) when creating a new pair.

## Writing skills (required before review)

Refine wording with the appropriate skill **before** asking for review. Do not skip this for new or substantially edited drafts.

| Language | Skill | Purpose / source |
| :--- | :--- | :--- |
| Japanese | `japanese-tech-writing` | Japanese technical prose. Source: https://gist.github.com/k16shikano/fd287c3133457c4fd8f5601d34aa817d |
| English | `humanizer` | Remove sentence-level AI-writing tells. Source: https://github.com/blader/humanizer |
| English | `english-tech-blog-structure` | Article structure for tech posts. Source: https://github.com/yohei1126/agent-skills/tree/main/english-tech-blog-structure (adapted from getsentry/skills blog-writing-guide: https://github.com/getsentry/skills/blob/main/skills/blog-writing-guide/SKILL.md) |

For English LinkedIn articles/posts, apply **both** `humanizer` and `english-tech-blog-structure` before review.

## Lint before push

Run markdownlint locally before pushing:

```bash
npm install
npm run lint
```

Config is `.markdownlint.json` (based on yohei1126/zenn; line length and LinkedIn-prose-friendly rules are relaxed). CI runs the same check via `.github/workflows/markdownlint.yml`.

## External repos

| URL | Role |
| :--- | :--- |
| [yohei1126/zenn](https://github.com/yohei1126/zenn) | Zenn series manuscripts (`articles/`) and planning (`instructions/`) |
| [edgesentry/ontographia](https://github.com/edgesentry/ontographia) | Open-source project referenced by the Ontographia LinkedIn drafts |

## Success criteria for edits

- Filenames match the convention above.
- Wording refined with the skills above before review.
- `npm run lint` / CI markdownlint passes.
- LinkedIn drafts remain English Markdown suitable for manual paste/publish.
- No Zenn-only tooling or season-plan workflow is assumed here.
