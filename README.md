# writing

Markdown sources for Yohei’s non-Zenn outreach writing (LinkedIn now; later X posts, talk drafts, etc.).

## Layout

| Path | Contents |
| :--- | :--- |
| `linkedin/` | LinkedIn long-form articles and feed post drafts (English) |
| `linkedin/ontographia/` | Ontographia series (Parts 1–3 article/post pairs) |
| `devto/` | Dev.to registration metadata only (`published: false`). Article body stays in `linkedin/`. |
| `devto/ontographia/` | Ontographia Dev.to meta (Part 1) |
| `scripts/devto_payload.py` | Prints a Dev.to payload JSON from a meta file and the LinkedIn article. Does not publish. |

Zenn articles stay in [yohei1126/zenn](https://github.com/yohei1126/zenn). This repo does not publish automatically — the author posts manually to each platform. Dev.to registration is a separate step after merge; `devto/` does not call the API.

Build a payload (still no API call):

```bash
python3 scripts/devto_payload.py devto/ontographia/2026-09-08-ontographia-part1-template-cost.yml
```

## LinkedIn naming

```text
linkedin/YYYY-MM-DD-slug-{article|post}.en.md
linkedin/<series>/YYYY-MM-DD-<series>-partN-<topic-slug>-{article|post}.en.md
```

- `*-article.en.md` — LinkedIn article (long form)
- `*-post.en.md` — feed post draft

Multi-part series use a named subfolder. Part order shows in the filename via `partN`.

Example: `linkedin/ontographia/2026-09-08-ontographia-part1-template-cost-article.en.md`
