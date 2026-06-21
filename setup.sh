#!/bin/sh
# seoclaw onboarding — the simplified, SEO-only setup flow.
#
# This REPLACES `zeroclaw quickstart`: instead of asking about providers, risk
# profiles, memory backends and 30 channels, it asks the two things an SEO user
# needs (a Codex login + the OpenSEO endpoint) and renders a ready config.
#
# Idempotent: safe to re-run to reconfigure. Run via install.sh, or directly.
set -eu

REPO_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

# seoclaw owns its own config/data namespace so it never collides with a
# stock ~/.zeroclaw install on the same machine.
ZEROCLAW_CONFIG_DIR="${ZEROCLAW_CONFIG_DIR:-$HOME/.seoclaw}"
ZEROCLAW_DATA_DIR="${ZEROCLAW_DATA_DIR:-$ZEROCLAW_CONFIG_DIR/data}"
export ZEROCLAW_CONFIG_DIR ZEROCLAW_DATA_DIR

CONFIG_FILE="$ZEROCLAW_CONFIG_DIR/config.toml"
TEMPLATE="$REPO_DIR/config/seoclaw.toml.tmpl"
SKILLS_DIR="$REPO_DIR/skills/seo"
DEFAULT_OPENSEO_URL="https://mcp.openseo.com/mcp"   # verify against your OpenSEO account

say() { printf '\033[1;36m▸ %s\033[0m\n' "$1"; }
err() { printf '\033[1;31m✗ %s\033[0m\n' "$1" >&2; }

command -v zeroclaw >/dev/null 2>&1 || {
  err "zeroclaw not found on PATH. Run ./install.sh first (it installs the pinned binary)."
  exit 1
}

say "seoclaw setup"
echo "  Config dir : $ZEROCLAW_CONFIG_DIR"
echo "  Skills     : $SKILLS_DIR"
echo

# ── 1. OpenSEO endpoint ────────────────────────────────────────────────────
printf 'OpenSEO MCP endpoint URL [%s]: ' "$DEFAULT_OPENSEO_URL"
read -r OPENSEO_URL || true
[ -n "${OPENSEO_URL:-}" ] || OPENSEO_URL="$DEFAULT_OPENSEO_URL"

# ── 2. Render config from template ─────────────────────────────────────────
say "Writing $CONFIG_FILE"
mkdir -p "$ZEROCLAW_CONFIG_DIR" "$ZEROCLAW_DATA_DIR"
# Use | as the sed delimiter since values contain /.
sed -e "s|__SKILLS_DIR__|$SKILLS_DIR|g" \
    -e "s|__OPENSEO_URL__|$OPENSEO_URL|g" \
    "$TEMPLATE" > "$CONFIG_FILE"

# ── 3. OpenAI Codex subscription login ─────────────────────────────────────
# Codex sub auth uses a stored login profile, not an api_key (see README).
say "Authenticating OpenAI Codex subscription"
if [ -f "$HOME/.codex/auth.json" ]; then
  echo "  Found ~/.codex/auth.json — importing existing Codex login."
  zeroclaw auth login --model-provider openai-codex --import "$HOME/.codex/auth.json"
else
  echo "  No ~/.codex/auth.json found. Starting an interactive Codex login."
  echo "  (Use the browser flow it prints; --device-code is available for headless boxes.)"
  zeroclaw auth login --model-provider openai-codex || {
    err "Codex login did not complete. Re-run: zeroclaw auth login --model-provider openai-codex"
    err "Then check: zeroclaw auth status"
    exit 1
  }
fi

# ── 4. Verify ──────────────────────────────────────────────────────────────
say "Verifying auth"
zeroclaw auth status || true

echo
say "Done. Start the SEO claw with:"
echo "    bin/seoclaw agent -a seo      # branded wrapper (sets the config dir for you)"
echo "    ZEROCLAW_CONFIG_DIR=$ZEROCLAW_CONFIG_DIR zeroclaw agent -a seo"
