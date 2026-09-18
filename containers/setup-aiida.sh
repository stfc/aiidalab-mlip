#!/usr/bin/env bash
# setup-aiida.sh — run inside the demo container to configure AiiDA for the
# aiidalab-mlip app. It is idempotent so it is safe to run more than once.
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-$(command -v python3)}"
AIIDA_DB_HOST="${AIIDA_DB_HOST:-localhost}"
AIIDA_DB_PORT="${AIIDA_DB_PORT:-5432}"
AIIDA_DB_NAME="${AIIDA_DB_NAME:-aiida}"
AIIDA_DB_USER="${AIIDA_DB_USER:-aiida}"
AIIDA_DB_PASS="${AIIDA_DB_PASS:-aiida}"

# ── Locate the janus binary ─────────────────────────────────────────────────
JANUS_EXE="${JANUS_EXE:-}"
if [ -z "$JANUS_EXE" ]; then
    if command -v janus >/dev/null 2>&1; then
        JANUS_EXE="$(command -v janus)"
    else
        JANUS_EXE_FILE=$(mktemp)
        "$PYTHON_BIN" - > "$JANUS_EXE_FILE" <<'PY'
import shutil
import sys
import os

exe = shutil.which('janus')
if exe:
    print(exe)
else:
    candidate = os.path.join(os.path.dirname(sys.executable), 'janus')
    if os.path.isfile(candidate):
        print(candidate)
    else:
        raise SystemExit('janus binary not found')
PY
        JANUS_EXE=$(cat "$JANUS_EXE_FILE")
        rm -f "$JANUS_EXE_FILE"
    fi
fi

if [ ! -f "$JANUS_EXE" ]; then
    echo "ERROR: janus executable not found at $JANUS_EXE" >&2
    exit 1
fi

# ── Wait for an AiiDA profile to become available ──────────────────────────
# The AiiDAlab base image creates the profile when the container starts, so
# this script must be run after the container is alive.
wait_for_profile() {
    local attempts=30
    local i
    for i in $(seq 1 $attempts); do
        if verdi profile show default >/dev/null 2>&1; then
            return 0
        fi
        echo "Waiting for AiiDA profile... ($i/$attempts)"
        sleep 2
    done
    return 1
}

if ! wait_for_profile; then
    # Some AiiDAlab images defer profile creation until the first login. Try
    # to create a minimal profile ourselves using the standard full-stack
    # PostgreSQL/RabbitMQ credentials.
    echo "WARNING: no default profile found; attempting to create one..."
    mkdir -p /tmp/aiida-mlip-repository
    verdi profile setup core.psql_dos \
        --profile-name default \
        --set-as-default \
        --non-interactive \
        --database-hostname "$AIIDA_DB_HOST" \
        --database-port "$AIIDA_DB_PORT" \
        --database-name "$AIIDA_DB_NAME" \
        --database-username "$AIIDA_DB_USER" \
        --database-password "$AIIDA_DB_PASS" \
        --use-rabbitmq \
        --email "dev@local" \
        --first-name Dev \
        --last-name User \
        --institution Local \
        --repository-uri "file:///tmp/aiida-mlip-repository" \
        || {
            echo "ERROR: could not create AiiDA profile." >&2
            echo "       Make sure the container has started and services are ready." >&2
            exit 1
        }
fi

verdi profile setdefault default || true

# ── Set up a localhost computer for running calculations ────────────────────
if ! verdi computer show localhost >/dev/null 2>&1; then
    verdi computer setup \
        --label localhost \
        --hostname localhost \
        --transport core.local \
        --scheduler core.direct \
        --work-dir /tmp/aiida-mlip-runs \
        --mpirun-command "" \
        --non-interactive
    verdi computer configure core.local localhost --non-interactive --safe-interval 0
fi

# ── Register the janus code in AiiDA ─────────────────────────────────────────
if ! verdi code show janus@localhost >/dev/null 2>&1; then
    verdi code create core.code.installed \
        --non-interactive \
        --label janus \
        --computer localhost \
        --filepath-executable "$JANUS_EXE" \
        --description "Janus MLIP executable from janus-core"
fi

# ── Register the venv Python for scripts / utilities ────────────────────────
if ! verdi code show python3@localhost >/dev/null 2>&1; then
    verdi code create core.code.installed \
        --non-interactive \
        --label python3 \
        --computer localhost \
        --filepath-executable "$PYTHON_BIN" \
        --description "Python 3"
fi

# ── Start the AiiDA daemon ────────────────────────────────────────────────
if ! verdi daemon status 2>/dev/null | grep -q "Daemon is running"; then
    verdi daemon start 2
fi

echo ""
echo "=== aiidalab-mlip ready ==="
echo "  janus binary: $JANUS_EXE"
echo "  Python code : $PYTHON_BIN (python3@localhost)"
echo "  verdi shell : verdi shell"
