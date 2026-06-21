#!/bin/sh
# seoclaw installer.
#
# Two clearly separate steps:
#   1. Install the pinned, UNMODIFIED upstream ZeroClaw binary (a dependency).
#   2. Apply OUR overlay: render the seoclaw config and run the SEO onboarding.
#
# Nothing here patches ZeroClaw. We treat it like a pinned base image.
set -eu

REPO_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ZC_VERSION=$(cat "$REPO_DIR/.zeroclaw-version")
UPSTREAM_INSTALL="https://raw.githubusercontent.com/zeroclaw-labs/zeroclaw/master/install.sh"

SKIP_ZEROCLAW=0
for arg in "$@"; do
  case "$arg" in
    --skip-zeroclaw) SKIP_ZEROCLAW=1 ;;   # binary already installed; just apply overlay
    -h|--help)
      cat <<EOF
seoclaw installer

Usage: ./install.sh [--skip-zeroclaw]

  --skip-zeroclaw   Don't (re)install the zeroclaw binary; only apply the
                    seoclaw config overlay and run setup. Use when you already
                    have the pinned version ($ZC_VERSION) on PATH.

Env:
  ZEROCLAW_CONFIG_DIR   Where seoclaw's config lives (default: ~/.seoclaw)
EOF
      exit 0 ;;
  esac
done

say() { printf '\033[1;36m▸ %s\033[0m\n' "$1"; }

# ── 1. Install the pinned upstream binary ──────────────────────────────────
if [ "$SKIP_ZEROCLAW" -eq 0 ]; then
  if command -v zeroclaw >/dev/null 2>&1 && [ "$(zeroclaw --version 2>/dev/null | awk '{print $NF}')" = "${ZC_VERSION#v}" ]; then
    say "zeroclaw ${ZC_VERSION} already installed — skipping."
  else
    say "Installing upstream zeroclaw ${ZC_VERSION} (unmodified dependency)"
    # Upstream installer; --skip-quickstart because OUR setup.sh handles onboarding.
    curl -fsSL "$UPSTREAM_INSTALL" | sh -s -- --prebuilt --skip-quickstart || {
      printf '\033[1;31m✗ upstream install failed. Install zeroclaw %s manually, then re-run with --skip-zeroclaw\033[0m\n' "$ZC_VERSION" >&2
      exit 1
    }
  fi
else
  say "Skipping zeroclaw install (--skip-zeroclaw)."
fi

# ── 2. Apply our overlay (config + onboarding) ─────────────────────────────
say "Applying seoclaw overlay"
chmod +x "$REPO_DIR/bin/seoclaw" "$REPO_DIR/setup.sh" 2>/dev/null || true
exec "$REPO_DIR/setup.sh"
