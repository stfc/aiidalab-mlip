# Dockerfile for the aiidalab-mlip AiiDAlab deployment image.
#
# Builds a self-contained AiiDAlab image with the aiidalab-mlip app baked in,
# based on the STFC ALC-UX Python 3.10 port of the official AiiDAlab
# full-stack image (ghcr.io/stfc/alc-ux/base:py310).
#
# Install:
#   podman build -f containers/Dockerfile -t aiidalab-mlip:latest .
#   (or run ./containers/build.sh)
#
# Run:
#   podman run -it --rm -p 8888:8888 -v "$HOME":/home/jovyan aiidalab-mlip:latest
#   (or use ./containers/startup.sh)

FROM ghcr.io/stfc/alc-ux/base:py310

USER root

# ---------------------------------------------------------------------------
# Dependencies & Constraints
# ---------------------------------------------------------------------------
# The base image pins aiida-core==2.7.1 in /opt/requirements.txt via PIP_CONSTRAINT.
# aiida-mlip requires aiida-core~=2.7.4, so we remove the strict aiida-core pin.
RUN sed -i '/aiida-core/d' /opt/requirements.txt

# Install aiida-mlip, alc-aiidalab-widgets (add-parameters branch providing layouts.WizardStep),
# janus-core with MACE support, backports.tarfile, and aiida-core[rest] (for verdi restapi).
# ``--pre`` allows alpha pre-releases if needed.
RUN pip install --no-cache-dir --no-user --pre \
        "git+https://github.com/stfc/aiida-mlip.git" \
        "git+https://github.com/stfc/alc-aiidalab-widgets.git@add-parameters" \
        "janus-core[mace]" \
        "backports.tarfile" \
        "aiida-core[rest]" && \
    F="$(find /opt/conda -name 'layouts.py' -path '*/alc_aiidalab_widgets/*')" && \
    if [ -n "$F" ] && ! grep -q 'from __future__ import annotations' "$F"; then \
        sed -i '1s|^|from __future__ import annotations\n|' "$F"; \
    fi && \
    jupyter serverextension disable --sys-prefix jupyter_lsp

# ---------------------------------------------------------------------------
# The AiiDAlab app
# ---------------------------------------------------------------------------
# We install the app into /opt (system space) and let the first-boot hook
# symlink it into <home>/apps/aiidalab-mlip. This mirrors how the base image
# installs its own home app and ensures the app remains discoverable even when
# the user's home directory is bind-mounted for data persistence (a fresh bind
# would otherwise shadow anything baked into /home/jovyan/apps).
# Ownership and group-write permissions are granted so that AppMode and Jupyter
# can create temporary notebooks (e.g. .main-0.ipynb) and checkpoints.
COPY . /opt/aiidalab-mlip/app
RUN pip install --no-cache-dir --no-user --pre /opt/aiidalab-mlip/app && \
    chown -R ${NB_UID}:${NB_GID} /opt/aiidalab-mlip && \
    chmod -R g+rwXs /opt/aiidalab-mlip

# ---------------------------------------------------------------------------
# First-boot / every-boot AiiDA setup
# ---------------------------------------------------------------------------
# The base image's before-notebook.d hooks already create the AiiDA profile +
# localhost computer (40_prepare-aiida.sh) and start the daemon
# (90_start_aiida_daemon.sh). Our hook (95_*, numeric ordering) runs after them
# to register the janus + python3 codes and start the REST API the app needs.
# All referenced scripts are idempotent, so they are safe on every start.
COPY containers/setup-aiida.sh /opt/aiidalab-mlip/setup-aiida.sh
COPY containers/start_restapi.sh /opt/aiidalab-mlip/start_restapi.sh
COPY containers/95_setup-aiidalab-mlip.sh \
    /usr/local/bin/before-notebook.d/95_setup-aiidalab-mlip.sh
RUN chmod +x /opt/aiidalab-mlip/*.sh \
    /usr/local/bin/before-notebook.d/95_setup-aiidalab-mlip.sh && \
    chown -R ${NB_UID}:${NB_GID} /opt/aiidalab-mlip

# ---------------------------------------------------------------------------
# Restore the non-root runtime user
# ---------------------------------------------------------------------------
USER ${NB_UID}
WORKDIR ${HOME}
