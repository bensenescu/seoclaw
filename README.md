# seoclaw

**Your autonomous SEO teammate.**

seoclaw is an opinionated SEO agent that does the work: keyword research,
competitor analysis, link prospecting, and keeping an eye on Search Console. Talk
to it in your terminal — or from Telegram, Slack, or Discord — and leave it
running so it works on a schedule while you sleep.

It's built on [Hermes Agent](https://github.com/NousResearch/hermes-agent) and
ships ready to go: a tuned SEO persona, live SEO data via OpenSEO, and a bundle
of SEO skills. No setup beyond two sign-ins.

## What it does

- **Keyword research & clustering** — find opportunities and map them to pages
- **Competitor & landscape analysis** — see who's winning and where your gaps are
- **Link prospecting** — surface link opportunities and draft outreach
- **Search Console watch** — catch ranking drops and striking-distance wins
- **Coaching & onboarding** — walks you through strategy and setup

## Install

```bash
# 1. Install Hermes (skip if you already have it)
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash

# 2. Install seoclaw
hermes profile install github.com/bensenescu/seoclaw --alias

# 3. Sign in (one-time, stored privately on your machine)
hermes -p seoclaw auth add openai-codex   # the model — OpenAI Codex
hermes -p seoclaw mcp login openseo       # your SEO data — OpenSEO

# 4. Talk to it
seoclaw
```

It runs as its own isolated profile — no env vars to manage, and it won't touch
the rest of your Hermes setup.

## Put it on autopilot

Leave it running and it works on a schedule, pinging you on your chat app:

```bash
seoclaw gateway   # keep it on; reach it from Telegram, Slack, Discord…
seoclaw cron create "every 1d" "Flag Search Console pages that dropped in clicks or position since yesterday."
seoclaw cron list
```

## Customize

Fork it and edit `config.yaml` (model, approvals), `SOUL.md` (persona), or
`skills/`, then re-install your fork. Or run `seoclaw model` to switch models.

## Develop & test locally

Install your working tree as a separate test profile — no push needed:

```bash
hermes profile install . --name seoclaw-dev    # `.` = this repo; --name keeps it separate
hermes -p seoclaw-dev auth add openai-codex
hermes -p seoclaw-dev mcp login openseo
hermes -p seoclaw-dev                           # chat

hermes profile update seoclaw-dev               # pull your edits in (add --force-config for config.yaml)
hermes profile delete seoclaw-dev --yes         # tear down
```

`profile update` re-pulls from your working tree, so the edit → test loop needs
no commit or push.

## License

MIT — see [LICENSE](LICENSE). Hermes Agent is MIT-licensed; the "Hermes" name
and logo are trademarks of Nous Research.
