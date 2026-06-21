#!/bin/sh
# seoclaw onboarding — the simplified, SEO-only setup flow.
#
# This REPLACES `zeroclaw quickstart`: instead of asking about providers, risk
# profiles, memory backends and 30 channels, it asks the two things an SEO user
# needs (the OpenSEO endpoint + a Codex sign-in) and writes a ready-to-run config.
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
DEFAULT_OPENSEO_URL="https://app.openseo.so/mcp"

bold() { printf '\033[1m%s\033[0m\n' "$1"; }
ok()   { printf '  \033[32m✓\033[0m %s\n' "$1"; }
step() { printf '\n\033[1;36m%s\033[0m\n' "$1"; }
fail() { printf '  \033[31m✗ %s\033[0m\n' "$1" >&2; }

command -v zeroclaw >/dev/null 2>&1 || {
  fail "zeroclaw isn't installed yet. Run ./install.sh first."
  exit 1
}

printf '\n'
bold "🔍  Setting up your SEO assistant"
printf "Two quick steps and you're ready to go.\n"

# ── Step 1: OpenSEO ─────────────────────────────────────────────────────────
step "Step 1 of 2 · Connect OpenSEO (your SEO data)"
printf '  OpenSEO endpoint [%s]: ' "$DEFAULT_OPENSEO_URL"
read -r OPENSEO_URL || true
[ -n "${OPENSEO_URL:-}" ] || OPENSEO_URL="$DEFAULT_OPENSEO_URL"

mkdir -p "$ZEROCLAW_CONFIG_DIR" "$ZEROCLAW_DATA_DIR"
# Use | as the sed delimiter since values contain /.
sed -e "s|__SKILLS_DIR__|$SKILLS_DIR|g" \
    -e "s|__OPENSEO_URL__|$OPENSEO_URL|g" \
    "$TEMPLATE" > "$CONFIG_FILE"
ok "OpenSEO connected"

# ── Step 2: OpenAI Codex sign-in ────────────────────────────────────────────
# Codex sub auth uses a stored login profile, not an api_key (see README).
step "Step 2 of 2 · Sign in to OpenAI Codex"
if [ -f "$HOME/.codex/auth.json" ]; then
  if zeroclaw auth login --model-provider openai-codex --import "$HOME/.codex/auth.json" >/dev/null 2>&1; then
    ok "Signed in with your existing Codex login"
  else
    fail "Couldn't reuse your Codex login. Try: zeroclaw auth login --model-provider openai-codex"
    exit 1
  fi
else
  printf '  No saved login found — opening the OpenAI sign-in flow...\n'
  zeroclaw auth login --model-provider openai-codex || {
    fail "Sign-in didn't finish. Just re-run ./setup.sh to try again."
    exit 1
  }
  ok "Signed in to OpenAI Codex"
fi

zeroclaw auth status >/dev/null 2>&1 || true

# ── Done ────────────────────────────────────────────────────────────────────
printf '\n'
bold "✅  All set — your SEO assistant is ready."
printf '\nStart chatting with it:\n'
printf '  \033[1mbin/seoclaw agent -a seo\033[0m\n\n'
