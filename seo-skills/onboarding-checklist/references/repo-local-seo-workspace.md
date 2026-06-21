# Repo-local SEO workspace pattern

Use this pattern when the user asks to “set up this workspace” or otherwise indicates the current repo/project should hold SEO working files.

## Folder location

Prefer:

```text
seo/<domain>/
```

Example:

```text
seo/openseo.so/
```

This keeps SEO strategy and exports near the site/product work without mixing them into the repo root.

## Starter structure

```text
seo/<domain>/
  README.md
  intake.md
  .gitignore
  gsc/
  keywords/
  competitors/
  content/
  outreach/
  reports/
  site-inventory/
```

## Recommended file roles

- `README.md`: setup checklist, sources checked, positioning notes, working assumptions, next workflows.
- `intake.md`: goals, audience, competitors, positioning boundaries, do-not-target notes.
- `gsc/README.md`: expected Search Console export names and how the data will be used.
- `keywords/README.md`: seed themes and later keyword exports/clusters.
- `competitors/README.md`: competitor/substitute list and analysis expectations.
- `content/README.md`: content inventory, page-to-keyword maps, briefs, refresh notes.
- `outreach/README.md`: linkable assets, prospecting angles, outreach drafts.
- `reports/README.md`: periodic summaries and decision logs.
- `site-inventory/README.md`: sitemap, crawl, canonical/indexability inventory.

## Local git hygiene

Add a workspace-local `.gitignore` to keep raw SEO exports local by default:

```gitignore
gsc/*.csv
gsc/*.tsv
gsc/*.xlsx
reports/*.csv
reports/*.xlsx
site-inventory/*.csv
site-inventory/*.xlsx
competitors/*.csv
keywords/*.csv
outreach/*.csv
*.har
*.log
```

The user can still intentionally commit curated markdown, briefs, and decision logs.

## Verification note

Before finalizing, verify with file listing/readback and git status when available. Report:

- exact workspace path
- key files created
- live sources checked, if any
- MCP/project status
- whether GSC exports are present
- one recommended next workflow
