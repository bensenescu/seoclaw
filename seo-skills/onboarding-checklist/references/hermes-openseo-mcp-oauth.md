# OpenSEO MCP OAuth note

Session learning: the OpenSEO hosted MCP endpoint can appear in `hermes mcp list`
as enabled while still being unusable if OAuth login hasn't been completed.

## Symptom

`hermes mcp test openseo` returns either:

- `401 Unauthorized` when the config only has the URL (no `auth: oauth`), or
- `MCP OAuth for 'openseo': non-interactive environment and no cached tokens found`
  when `auth: oauth` is set but the first-time login hasn't been done.

And if `hermes` reports `Server 'openseo' not found in config` or
`No MCP servers configured`, the issue is upstream of OAuth: `HERMES_HOME` isn't
pointed at the seoclaw repo. Run `export HERMES_HOME="$PWD"` from the repo root
(or `direnv allow`) and retry.

## Correct config

The repo's `config.yaml` already ships this shape — keep it:

```yaml
mcp_servers:
  openseo:
    url: https://app.openseo.so/mcp
    auth: oauth
```

## Verification flow

From the seoclaw repo, with `HERMES_HOME` set:

```bash
hermes mcp list
hermes mcp test openseo
```

If OAuth tokens are missing, complete the login interactively:

```bash
hermes mcp login openseo
```

A tool/non-interactive environment may not be able to open/complete the browser
OAuth approval. In that case, explain the exact login command and have the user
complete it in their terminal before starting a fresh session.
