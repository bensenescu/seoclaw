# seoclaw

A claw that handles SEO for your website.

**seoclaw is a configuration overlay on top of [ZeroClaw](https://github.com/zeroclaw-labs/zeroclaw).**
We don't fork ZeroClaw and we don't patch it. We install the unmodified upstream
binary (pinned in [`.zeroclaw-version`](.zeroclaw-version)) and hand it a
ready-made config plus a bundle of SEO skills. Think of ZeroClaw as a base image
and this repo as the layer on top.

## What's ours vs. what's ZeroClaw

| Ours (this repo) | ZeroClaw (upstream, unmodified) |
| --- | --- |
| `config/seoclaw.toml.tmpl` — the agent, provider, risk profile, MCP + skill wiring | The runtime that reads that config |
| `skills/seo/` — the OpenSEO skill bundle | The skill loader that runs them |
| `setup.sh` — the simplified SEO onboarding | `zeroclaw quickstart` (we don't use it) |
| `install.sh` — installs the pinned binary, then applies our overlay | The `zeroclaw` binary it installs |
| `bin/seoclaw` — light-touch branded wrapper | The `zeroclaw` command it forwards to |

If it's behavior, it's upstream. If it's SEO content or wiring, it's here. The
only coupling point is ZeroClaw's config schema, which is a documented, validated,
stable interface — so we pin a version and bump it deliberately.

## Install

```bash
./install.sh
```

This:
1. Installs the pinned upstream ZeroClaw binary (`v0.8.1`) — skipped if already present.
2. Runs `setup.sh`, which asks the **two** things an SEO user needs.

Already have the pinned binary? `./install.sh --skip-zeroclaw`.

## Onboarding (the simplified flow)

`setup.sh` replaces ZeroClaw's full `quickstart`. It asks only:

1. **OpenSEO MCP endpoint URL** (the only SEO integration).
2. **OpenAI Codex subscription login** — the only provider. Codex sub auth uses a
   stored login profile, **not** an API key: setup runs
   `zeroclaw auth login --model-provider openai-codex` (or imports an existing
   `~/.codex/auth.json`). The config sets `requires_openai_auth = true` so the
   runtime reads that login. See ZeroClaw's README "OpenAI Codex subscription" note.

No questions about memory, channels, or the other ~20 providers — they're simply
never surfaced because we ship a complete config instead of generating one.

## Run

```bash
bin/seoclaw agent -a seo
```

The `bin/seoclaw` wrapper sets `ZEROCLAW_CONFIG_DIR=~/.seoclaw` (isolated from any
stock `~/.zeroclaw` on the machine) and forwards to the real `zeroclaw` binary.
For interactive `agent` runs it also defaults to a persistent session file
(`~/.seoclaw/seo-session.json`) so the conversation survives a restart — which
you need whenever you change config. Equivalent without the wrapper:

```bash
ZEROCLAW_CONFIG_DIR=~/.seoclaw zeroclaw agent -a seo --session-state-file ~/.seoclaw/seo-session.json
```

Inside the REPL: `/exit` or `/quit` to leave (Ctrl-D also works), `/help` for
commands, `/clear` to wipe the conversation, `/think:<level>` to change
reasoning depth on the fly. Config edits are picked up on the next launch, not
mid-session.

## Layout

```
seoclaw/
├── .zeroclaw-version          # pinned upstream version we certify against
├── install.sh                 # 1) install pinned zeroclaw  2) run setup
├── setup.sh                   # SEO-only onboarding (renders config + Codex login)
├── bin/seoclaw                # branded wrapper around `zeroclaw`
├── config/
│   └── seoclaw.toml.tmpl       # config template (rendered into ~/.seoclaw/config.toml)
└── skills/seo/                # OpenSEO skill bundle (loaded by the agent)
    ├── keyword-research/
    ├── keyword-clustering/
    ├── competitor-analysis/
    ├── competitive-landscape/
    ├── link-prospecting/
    ├── seo-coach/
    └── onboarding-checklist/
```

## Upgrading ZeroClaw

Bump `.zeroclaw-version`, re-run `./install.sh`, and re-test. Because our only
dependency on upstream is the config schema, upgrades are low-risk; check the
ZeroClaw changelog for any config-schema changes between versions.

## License

MIT — see [LICENSE](LICENSE). ZeroClaw is dual-licensed MIT OR Apache-2.0; the
"ZeroClaw" name and logo are trademarks of ZeroClaw Labs.
