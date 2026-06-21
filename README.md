# seoclaw

An opinionated SEO agent you can **clone and run** on top of
[Hermes Agent](https://github.com/NousResearch/hermes-agent). It ships a tuned
config, an SEO persona, the OpenSEO MCP integration, and a bundle of SEO skills
(keyword research, clustering, competitor & competitive-landscape analysis, link
prospecting, coaching, onboarding) — so you don't have to configure any of it.

This repo is a **configuration overlay**, not a fork: it runs the unmodified
`hermes` command and just hands it a ready-made config + skills. The repo
itself is the Hermes home — you point `HERMES_HOME` at it and run `hermes`.

## Quick start

```bash
# 1. Clone
git clone <repo-url> seoclaw
cd seoclaw

# 2. Install Hermes (skip if you already have it)
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash

# 3. Use this repo as your Hermes home
export HERMES_HOME="$PWD"

# 4. One-time sign-in: OpenAI Codex (offers to import an existing ~/.codex/auth.json)
hermes auth add openai-codex

# 5. Run it
hermes
```

`export HERMES_HOME="$PWD"` is the one thing to remember: it tells stock Hermes
to read this repo's `config.yaml`, `SOUL.md`, and `seo-skills/` instead of your
default `~/.hermes`. Set it once per shell from the repo root — or add it to
your shell rc, or use an alias:

```bash
alias seoclaw='HERMES_HOME=/path/to/seoclaw hermes'
```

The first time you ask for SEO data, OpenSEO runs a one-time in-conversation
OAuth (a browser approval). If an OpenSEO call ever returns `401 Unauthorized`,
complete the login explicitly with `hermes mcp login openseo`.

## How it works

It's stock Hermes pointed at this repo — no scripts, no magic:

- **`config.yaml`** and **`SOUL.md`** sit at the repo root, exactly where Hermes
  reads a home's config and persona from.
- **`seo-skills/`** is loaded via `skills.external_dirs` (Hermes' standard way to
  add skills), so the bundle lives in the repo and the bundled Hermes skills stay
  available alongside it.
- **Everything Hermes writes** — auth tokens, session history, caches, the synced
  bundled-skill library — lands in this dir at runtime and is git-ignored by an
  allowlist `.gitignore`, so nothing you run can be committed by accident.

Edit a `seo-skills/**/SKILL.md`, `config.yaml`, or `SOUL.md` and just relaunch.

### Make it yours

It's a scaffold — fork it and edit:

- **Model / provider** — change the two `model:` lines in `config.yaml`, or run
  `hermes model`. (Default is the OpenAI Codex subscription, `gpt-5.5`.)
- **Persona** — edit `SOUL.md`.
- **Skills** — add or edit folders under `seo-skills/` (each is a `SKILL.md`).
- **Approvals** — `approvals.mode` in `config.yaml` (`manual` / `smart` / `off`).

> On a Hermes version newer than this repo targets, Hermes normalizes
> `config.yaml` on first run (a format bump). That's expected — keep or discard
> the diff.

## Layout

```
seoclaw/
├── config.yaml          # the Hermes config (provider, agent, skills, OpenSEO MCP)
├── SOUL.md              # the SEO assistant persona
├── seo-skills/          # the SEO skill bundle (loaded via skills.external_dirs)
│   ├── keyword-research/
│   ├── keyword-clustering/
│   ├── competitor-analysis/
│   ├── competitive-landscape/
│   ├── link-prospecting/
│   ├── seo-coach/
│   └── onboarding-checklist/
├── .gitignore           # allowlist: commits the scaffold, ignores all runtime
└── (runtime, git-ignored: auth, sessions, caches, synced bundled skills, …)
```

## Optional: always-on scheduled checks

To add recurring SEO checks, run the always-on gateway and schedule tasks (stock
Hermes cron, with `HERMES_HOME` pointed at this repo):

```bash
hermes gateway                                   # always-on (messaging + cron host)
hermes cron create "every 1d" "Check Search Console for pages that dropped in clicks or position since yesterday and flag the biggest losers."
hermes cron list
```

## License

MIT — see [LICENSE](LICENSE). Hermes Agent is MIT-licensed; the "Hermes" name
and logo are trademarks of Nous Research.
