# seoclaw

An opinionated SEO agent for [Hermes Agent](https://github.com/NousResearch/hermes-agent).

It's a **Hermes profile distribution**: install it with one command and you get a
tuned SEO persona, the OpenSEO MCP integration, and a bundle of SEO skills
(keyword research, clustering, competitor & competitive-landscape analysis, link
prospecting, coaching, onboarding) — as an isolated profile that never touches
your default Hermes setup.

## Install

```bash
# 1. Install Hermes (skip if you already have it)
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash

# 2. Install the seoclaw profile (from GitHub — or a local clone)
hermes profile install <repo-url> --alias
#   local dev:  hermes profile install /path/to/seoclaw --alias

# 3. One-time sign-ins (stored per-profile, never committed)
hermes -p seoclaw auth add openai-codex   # the model: OpenAI Codex (imports ~/.codex/auth.json if present)
hermes -p seoclaw mcp login openseo       # the SEO data: OpenSEO — approve in the browser

# 4. Run it — `--alias` created a `seoclaw` command:
seoclaw
```

**No `HERMES_HOME`, no env vars.** The profile lives at
`~/.hermes/profiles/seoclaw/`, fully isolated from your default `~/.hermes`.

Don't want the alias? Either make it your sticky default
(`hermes profile use seoclaw`, then just run `hermes`), or pass `-p seoclaw` on
each command.

## Updating

```bash
hermes profile update seoclaw   # pulls new persona/skills; keeps your config, auth, and history
```

`config.yaml` is preserved on update (so your model tweaks survive); `SOUL.md`
and `skills/` are refreshed from the distribution. Your auth, memories, and
sessions are never touched.

## What's inside

```
seoclaw/
├── distribution.yaml   # profile manifest (name, version, requirements)
├── config.yaml         # model (OpenAI Codex / gpt-5.5), reasoning, approvals, OpenSEO MCP
├── SOUL.md             # the SEO assistant persona
└── skills/             # the SEO skill bundle
    ├── keyword-research/
    ├── keyword-clustering/
    ├── competitor-analysis/
    ├── competitive-landscape/
    ├── link-prospecting/
    ├── seo-coach/
    └── onboarding-checklist/
```

## Make it yours

It's a scaffold — fork the repo and edit `config.yaml`, `SOUL.md`, or `skills/`,
then re-install your fork (`hermes profile install <your-fork> --alias`). For
quick local tweaks, edit the installed copy under `~/.hermes/profiles/seoclaw/`
directly.

- **Model / provider** — the `model:` lines in `config.yaml`, or run `seoclaw model`.
- **Persona** — `SOUL.md`.
- **Skills** — add or edit folders under `skills/` (each is a `SKILL.md`).
- **Approvals** — `approvals.mode` in `config.yaml` (`manual` / `smart` / `off`).

## Optional: always-on scheduled checks

```bash
seoclaw gateway                                  # always-on (messaging + cron host)
seoclaw cron create "every 1d" "Check Search Console for pages that dropped in clicks or position since yesterday and flag the biggest losers."
seoclaw cron list
```

## License

MIT — see [LICENSE](LICENSE). Hermes Agent is MIT-licensed; the "Hermes" name
and logo are trademarks of Nous Research.
