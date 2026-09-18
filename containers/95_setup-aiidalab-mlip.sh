#!/bin/bash
# First-boot (and every-boot) setup for the aiidalab-mlip app.
#
# Dropped into /usr/local/bin/before-notebook.d/ and run as part of the image's
# container startup. The numeric prefix (95) ensures it runs AFTER the base
# image has prepared the home directory and AiiDA (40_prepare-aiida.sh creates
# the AiiDA profile + localhost computer, 60_prepare-aiidalab.sh installs the
# home app, 90_start_aiida_daemon.sh starts the AiiDA daemon).
#
# On every start it:
#   1. Links the app into <home>/apps/aiidalab-mlip (from system space), so it
#      stays discoverable even when the home directory is bind-mounted;
#   2. Runs the (idempotent) AiiDA setup: registers localhost "janus" and
#      "python3" codes if missing, and starts the AiiDA daemon if needed;
#   3. (Re)starts the AiiDA REST API used by the app widgets.
#
set -x
export SHELL=/bin/bash

# 1. Expose the app in user space (target the default jovyan home robustly).
# Only link when nothing exists yet, so a user's own install is never replaced.
HOME_DIR="${HOME:-/home/jovyan}"
APPS_DIR="${AIIDALAB_APPS:-${HOME_DIR}/apps}"
APP_DIR="${APPS_DIR}/aiidalab-mlip"
if [[ ! -e "${APP_DIR}" ]]; then
    mkdir -p "${APPS_DIR}"
    if [[ -d "/opt/aiidalab-mlip/app" ]]; then
        # Ensure app directory is writable by jovyan for AppMode temporary notebooks (.main-*.ipynb)
        chmod -R g+rwX /opt/aiidalab-mlip/app 2>/dev/null || true
        ln -sfn /opt/aiidalab-mlip/app "${APP_DIR}"
        echo "Linked aiidalab-mlip app at ${APP_DIR}"
    else
        echo "WARNING: app source missing at /opt/aiidalab-mlip/app" >&2
    fi
fi

# Clean up any stale temporary AppMode notebooks from prior runs
find -L "${APP_DIR}" -maxdepth 1 -type f -name '.*.ipynb' -delete 2>/dev/null || true

# 2 + 3. Idempotent AiiDA configuration (codes, daemon, REST API).
if /opt/aiidalab-mlip/setup-aiida.sh; then
    /opt/aiidalab-mlip/start_restapi.sh \
        || echo "WARNING: could not start AiiDA REST API" >&2
else
    echo "WARNING: AiiDA setup for aiidalab-mlip failed; see logs above." >&2
fi

# Never propagate a failure to the enclosing startup script (it is sourced by
# start.sh, which runs with `set -e`).
true
