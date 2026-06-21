# seoclaw

An opinionated SEO agent you can **clone and run** on top of
[Hermes Agent](https://github.com/NousResearch/hermes-agent). It ships a tuned
config, an SEO persona, the OpenSEO MCP integration, and a bundle of SEO skills
(keyword research, clustering, competitor & competitive-landscape analysis, link
prospecting, coaching, onboarding) — so you don't have to configure any of it.

This repo is a **configuration overlay**, not a fork: it runs the unmodified
`hermes` binary and just hands it a ready-made config + skills.

## Quick start

```bash
# 1. Clone
git clone <repo-url> seoclaw
cd seoclaw

# 2. Install Hermes (skip if you already have it)
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash

# 3. One-time sign-in: OpenAI Codex (offers to import an existing ~/.codex/auth.json)
bin/seoclaw auth add openai-codex

# 4. Run it
bin/seoclaw
```

That's the whole setup. The first time you ask for SEO data, OpenSEO runs a
one-time in-conversation OAuth (a browser approval). If an OpenSEO call ever
returns `401 Unauthorized`, complete the login explicitly:

```bash
bin/seoclaw mcp login openseo   # run interactively, approve in the browser
```

## How it works (no magic)

- **`bin/seoclaw`** is a ~25-line launcher. It points `HERMES_HOME` at a
  git-ignored `./.hermes-home/`, seeds your committed `config.yaml` + `SOUL.md`
  into it, then `exec`s stock `hermes`. You never set an env var, and it works
  from any directory.
- **All runtime state** — auth tokens, session history, caches, the synced
  bundled-skill library — lives in `./.hermes-home/` and is git-ignored.
  Combined with an allowlist `.gitignore`, nothing you run can be committed by
  accident.
- **The committed scaffold is just** `config.yaml`, `SOUL.md`, and `seo-skills/`.
  Edit a `seo-skills/**/SKILL.md` and relaunch — it's picked up live. If you edit
  `config.yaml` or `SOUL.md`, refresh the seeded copy:
  `rm .hermes-home/config.yaml .hermes-home/SOUL.md` then re-run `bin/seoclaw`.
- **Always launch via `bin/seoclaw`, not plain `hermes`** — plain `hermes` uses
  `~/.hermes` and won't load this repo's config, persona, or skills.

### Make it yours

It's a scaffold — fork it and edit:

- **Model / provider** — change the two `model:` lines in `config.yaml`, or run
  `bin/seoclaw model`. (Default is the OpenAI Codex subscription, `gpt-5.5`.)
- **Persona** — edit `SOUL.md`.
- **Skills** — add or edit folders under `seo-skills/` (each is a `SKILL.md`).
- **Approvals** — `approvals.mode` in `config.yaml` (`manual` / `smart` / `off`).

## Layout

```
seoclaw/
├── bin/seoclaw          # launcher: sets HERMES_HOME, seeds the home, runs hermes
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
└── .hermes-home/        # (git-ignored) Hermes' config copy, auth, sessions, caches
```

## Optional: always-on scheduled checks

seoclaw doesn't auto-create cron jobs (they're per-user runtime state). To add
recurring SEO checks yourself, run the always-on gateway and schedule tasks:

```bash
bin/seoclaw gateway                                   # always-on (messaging + cron host)
bin/seoclaw cron create "every 1d" "Check Search Console for pages that dropped in clicks or position since yesterday and flag the biggest losers."
bin/seoclaw cron list
```

## License

MIT — see [LICENSE](LICENSE). Hermes Agent is MIT-licensed; the "Hermes" name
and logo are trademarks of Nous Research.
