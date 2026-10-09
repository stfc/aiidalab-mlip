#!/usr/bin/env bash
# AiiDAlab MLIP startup script.
#
# Launches the aiidalab-mlip deployment image (or any AiiDAlab image) with
# data persistence, an AiiDA profile, and optional REST API port mapping.
# It detects and works with Podman, Docker, or Apptainer.
#
#   Usage:
#     ./startup.sh [options]
#
#   Options:
#     --image <name|path>     Container image (default: aiidalab-mlip:latest).
#                             As a name it is resolved via docker:// (Apptainer)
#                             or the local daemon (Podman/Docker). A *.sif path is used
#                             directly with Apptainer.
#     --engine <podman|docker|apptainer|auto>   Container engine (default: auto).
#     --port <host-port>      Host port for Jupyter (default: 8888).
#     --restapi-port <port>   Host port for the AiiDA REST API (default: 5050,
#                             pass 0 to disable).
#     --bind <path>           Host directory to persist as the container's
#                             /home/jovyan (default: $HOME).
#     --gpu                   Enable GPU passthrough (NVIDIA).
#     --no-profile-setup      Never attempt to create an AiiDA profile.
#     -h, --help              Show this help.
#
# If no AiiDA profile exists in the bind path, the script asks for the user's
# details and passes them to the container so it can create a profile on first
# start.
#
# NOTE: AiiDAlab images run as uid 1000 (jovyan). The --bind directory must be
# readable/writable by uid 1000. On Linux with Podman, --userns=keep-id is used
# automatically, or you can use `podman unshare chown 1000:100 <dir>`.
set -euo pipefail

IMAGE="${AIIDALAB_MLIP_IMAGE:-aiidalab-mlip:latest}"
ENGINE="${AIIDALAB_MLIP_ENGINE:-auto}"
PORT="${AIIDALAB_MLIP_PORT:-8888}"
RESTAPI_PORT="${AIIDALAB_MLIP_RESTAPI_PORT:-5050}"
BIND="${AIIDALAB_MLIP_BIND:-$HOME}"
USE_GPU="${AIIDALAB_MLIP_GPU:-0}"
SETUP_PROFILE=auto

usage() {
    # Print the leading "#" header block (usage text) of this script.
    awk 'NR > 1 { if (/^#/) { sub(/^# ?/, ""); print } else exit }' "$0"
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --image) IMAGE="$2"; shift 2 ;;
        --engine) ENGINE="$2"; shift 2 ;;
        --port) PORT="$2"; shift 2 ;;
        --restapi-port) RESTAPI_PORT="$2"; shift 2 ;;
        --bind) BIND="$2"; shift 2 ;;
        --gpu) USE_GPU=1; shift ;;
        --no-profile-setup) SETUP_PROFILE=no; shift ;;
        --help|-h) usage ;;
        *) echo "Unknown argument: $1" >&2; usage ;;
    esac
done

detect_engine() {
    case "$ENGINE" in
        auto)
            if command -v podman &>/dev/null; then
                ENGINE=podman
            elif command -v docker &>/dev/null; then
                ENGINE=docker
            elif command -v apptainer &>/dev/null; then
                ENGINE=apptainer
            else
                echo "ERROR: no supported container engine found (podman, docker, apptainer)." >&2
                exit 1
            fi
            ;;
    esac
    command -v "$ENGINE" &>/dev/null || {
        echo "ERROR: container engine '$ENGINE' not found on PATH." >&2
        exit 1
    }
}

# --- Container engine ---
detect_engine

# --- Data persistence bind path ---
if [[ ! -d "$BIND" ]]; then
    echo "ERROR: bind path '$BIND' does not exist." >&2
    exit 1
fi

# --- AiiDA profile ---
PROFILE_CONFIG="$BIND/.aiida/config.json"
AIIDA_PROFILE_NAME="${AIIDA_PROFILE_NAME:-default}"
AIIDA_ENV=()
if [[ "$SETUP_PROFILE" == no ]]; then
    AIIDA_ENV+=(--env "SETUP_DEFAULT_AIIDA_PROFILE=false")
    AIIDA_ENV+=(--env "AIIDA_PROFILE_NAME=${AIIDA_PROFILE_NAME}")
elif [[ -f "$PROFILE_CONFIG" ]]; then
    echo "Existing AiiDA profile detected; reusing it."
    AIIDA_ENV+=(--env "SETUP_DEFAULT_AIIDA_PROFILE=false")
    AIIDA_ENV+=(--env "AIIDA_PROFILE_NAME=${AIIDA_PROFILE_NAME}")
else
    echo "No existing AiiDA profile. Profile creation will be enabled;"
    echo "please provide the details used for the new profile."
    read -r -p "Email [aiida@localhost]: " AIIDA_USER_EMAIL
    AIIDA_USER_EMAIL="${AIIDA_USER_EMAIL:-aiida@localhost}"
    read -r -p "First name [Giuseppe]: " AIIDA_USER_FIRST_NAME
    AIIDA_USER_FIRST_NAME="${AIIDA_USER_FIRST_NAME:-Giuseppe}"
    read -r -p "Last name [Verdi]: " AIIDA_USER_LAST_NAME
    AIIDA_USER_LAST_NAME="${AIIDA_USER_LAST_NAME:-Verdi}"
    read -r -p "Institution [Khedivial]: " AIIDA_USER_INSTITUTION
    AIIDA_USER_INSTITUTION="${AIIDA_USER_INSTITUTION:-Khedivial}"
    AIIDA_ENV+=(--env "SETUP_DEFAULT_AIIDA_PROFILE=true")
    AIIDA_ENV+=(--env "AIIDA_PROFILE_NAME=${AIIDA_PROFILE_NAME}")
    AIIDA_ENV+=(--env "AIIDA_USER_EMAIL=${AIIDA_USER_EMAIL}")
    AIIDA_ENV+=(--env "AIIDA_USER_FIRST_NAME=${AIIDA_USER_FIRST_NAME}")
    AIIDA_ENV+=(--env "AIIDA_USER_LAST_NAME=${AIIDA_USER_LAST_NAME}")
    AIIDA_ENV+=(--env "AIIDA_USER_INSTITUTION=${AIIDA_USER_INSTITUTION}")
fi

# --- Compose and run the container ---
if [[ "$ENGINE" == "podman" || "$ENGINE" == "docker" ]]; then
    port_args=(-p "${PORT}:8888")
    [[ "$RESTAPI_PORT" != 0 ]] && port_args+=(-p "${RESTAPI_PORT}:5000")
    extra_args=()
    if [[ "$ENGINE" == "podman" ]]; then
        # Rootless Podman: map host user to container jovyan (uid 1000, gid 100)
        extra_args+=(--userns=keep-id:uid=1000,gid=100)
        extra_args+=(--security-opt seccomp=unconfined)
        if [[ "$USE_GPU" == 1 ]]; then
            # Support NVIDIA GPUs via CDI or --gpus
            extra_args+=(--device nvidia.com/gpu=all)
        fi
    else
        if [[ "$USE_GPU" == 1 ]]; then
            extra_args+=(--gpus all)
        fi
    fi
    echo "=== Running AiiDAlab MLIP with ${ENGINE} (image: $IMAGE) ==="
    exec "$ENGINE" run -it --rm \
        "${port_args[@]}" \
        "${extra_args[@]}" \
        -v "${BIND}:/home/jovyan:Z" \
        "${AIIDA_ENV[@]}" \
        "$IMAGE"
else
    apptainer_args=(--compat --cleanenv --home /home/jovyan --bind "${BIND}:/home/jovyan")
    if [[ "$USE_GPU" == 1 ]]; then
        apptainer_args+=(--nv)
    fi
    [[ "$IMAGE" == *.sif ]] && uri="$IMAGE" || uri="docker://${IMAGE}"
    echo "=== Running AiiDAlab MLIP with Apptainer (image: $uri) ==="
    exec apptainer run \
        "${apptainer_args[@]}" \
        "${AIIDA_ENV[@]}" \
        "$uri"
fi
