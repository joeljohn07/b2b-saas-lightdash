#!/usr/bin/env bash
# Bring the Lightdash stack up/down with secrets sourced from macOS Keychain.
#
# Why this exists: the project's pre-commit hook (and the user's global
# secrets policy) prevents persisting a .env file with real values. Instead,
# LIGHTDASH_SECRET and PGPASSWORD live in Keychain and are injected as env
# vars only at compose-runtime — never written to disk in this repo.
#
# Usage:
#   scripts/lightdash-stack.sh up [-d]    # bring stack up
#   scripts/lightdash-stack.sh down [-v]  # stop (with -v: also drop volume)
#   scripts/lightdash-stack.sh logs       # tail lightdash service
#   scripts/lightdash-stack.sh ps         # status
#
# Required Keychain entries (one-time setup via `security add-generic-password`):
#   - lightdash-secret      : 64-char hex (LIGHTDASH_SECRET)
#   - lightdash-pgpassword  : strong password (PGPASSWORD)
#
# Required env vars at call time:
#   - GCP_PROJECT_ID  : your BigQuery project ID

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# --- Source secrets from Keychain ---
LIGHTDASH_SECRET="$(security find-generic-password -s 'lightdash-secret' -a "$USER" -w 2>/dev/null)" || {
    echo "ERROR: lightdash-secret not found in Keychain." >&2
    echo "  Create it with:  security add-generic-password -s 'lightdash-secret' -a \"\$USER\" -w \"\$(openssl rand -hex 32)\"" >&2
    exit 1
}

PGPASSWORD="$(security find-generic-password -s 'lightdash-pgpassword' -a "$USER" -w 2>/dev/null)" || {
    echo "ERROR: lightdash-pgpassword not found in Keychain." >&2
    echo "  Create it with:  security add-generic-password -s 'lightdash-pgpassword' -a \"\$USER\" -w \"\$(openssl rand -base64 24 | tr -d '/+=')\"" >&2
    exit 1
}

if [[ -z "${GCP_PROJECT_ID:-}" ]]; then
    echo "WARN: GCP_PROJECT_ID is not set. Lightdash will fail to connect to BigQuery." >&2
    echo "      Export it before bringing up the stack:" >&2
    echo "        export GCP_PROJECT_ID=your-bq-project" >&2
fi

export LIGHTDASH_SECRET PGPASSWORD

# --- Dispatch ---
cmd="${1:-up}"
shift || true

case "$cmd" in
    up)
        # Default to detached mode for convenience
        if [[ $# -eq 0 ]]; then
            set -- -d
        fi
        docker compose up "$@"
        echo ""
        echo "Lightdash starting at http://localhost:${LIGHTDASH_PORT:-8080}"
        echo "Tail logs:   $(basename "$0") logs"
        echo "Stop stack:  $(basename "$0") down"
        ;;
    down)
        docker compose down "$@"
        ;;
    logs)
        docker compose logs -f lightdash "$@"
        ;;
    ps|status)
        docker compose ps
        ;;
    *)
        echo "Usage: $(basename "$0") {up [-d]|down [-v]|logs|ps}" >&2
        exit 2
        ;;
esac
