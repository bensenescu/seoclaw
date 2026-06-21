# seoclaw

An opinionated SEO agent you can **clone and run** on top of
[Hermes Agent](https://github.com/NousResearch/hermes-agent). It ships a tuned
config, an SEO persona, the OpenSEO MCP integration, and a bundle of SEO skills
(keyword research, clustering, competitor & competitive-landscape analysis, link
prospecting, coaching, onboarding) — so you don't have to configure any of it.

This repo is a **configuration overlay**, not a fork: it runs the unmodified
`hermes` command and just hands it a ready-made config + skills. You work out of
this folder, and `hermes` reads its config from here.

## Quick start

```bash
# 1. Clone and enter the folder
git clone <repo-url> seoclaw
cd seoclaw

# 2. Install Hermes (skip if you already have it)
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash

# 3. Point Hermes at this folder (run once per shell, from the repo root)
export HERMES_HOME="$PWD"

# 4. One-time sign-ins
hermes auth add openai-codex    # the model: OpenAI Codex (imports ~/.codex/auth.json if present)
hermes mcp login openseo        # the SEO data: OpenSEO — approve in the browser

# 5. Start chatting
hermes
```

**Always run `hermes` from this folder with `HERMES_HOME` set** — that's what
makes it load this repo's `config.yaml`, `SOUL.md`, and `seo-skills/` instead of
your default `~/.hermes`. If you skip step 3 you'll see things like
`Server 'openseo' not found in config` or `No MCP servers configured` — that just
means `HERMES_HOME` isn't set in the current shell.

To set it automatically: this repo ships a `.envrc`, so if you have
[direnv](https://direnv.net), run `direnv allow` once and `HERMES_HOME` is set
whenever you're in the folder — no export to remember.

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
├── .envrc               # optional: direnv sets HERMES_HOME when you're in the folder
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
