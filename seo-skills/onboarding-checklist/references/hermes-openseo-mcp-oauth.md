# Hermes/seoclaw OpenSEO MCP OAuth note

Session learning: the OpenSEO hosted MCP endpoint can appear in `hermes mcp list` as enabled while still being unusable if OAuth is not configured.

## Symptom

`./bin/seoclaw mcp test openseo` returns either:

- `401 Unauthorized` when the config only has the URL, or
- `MCP OAuth for 'openseo': non-interactive environment and no cached tokens found` when `auth: oauth` is set but first-time login has not been completed.

## Correct config

For seoclaw/Hermes, the hosted endpoint should be configured as:

```yaml
mcp_servers:
  openseo:
    url: https://app.openseo.so/mcp
    auth: oauth
```

The repo template should include the same shape so rerunning setup does not remove OAuth:

```yaml
mcp_servers:
  openseo:
    url: "__OPENSEO_URL__"
    auth: oauth
```

## Verification flow

From the seoclaw repo:

```bash
./bin/seoclaw mcp list
./bin/seoclaw mcp test openseo
```

If OAuth tokens are missing, ask the user to run the login interactively:

```bash
./bin/seoclaw mcp login openseo
```

A tool/non-interactive environment may not be able to open/complete the browser OAuth approval. In that case, fix the config, explain the exact login command, and have the user complete it in their terminal before starting a fresh seoclaw session.
