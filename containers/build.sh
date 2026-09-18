#!/usr/bin/env bash
# Build the aiidalab-mlip AiiDAlab deployment image.
#
# Usage:  ./containers/build.sh [--tag <tag>] [--no-cache] [-- <docker/podman build args>]
# Default tag: aiidalab-mlip:latest
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

TAG="aiidalab-mlip:latest"
BUILD_ARGS=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        --tag)
            TAG="$2"
            shift 2
            ;;
        --no-cache)
            BUILD_ARGS+=("--no-cache")
            shift
            ;;
        *)
            BUILD_ARGS+=("$1")
            shift
            ;;
    esac
done

# Use podman by default, or docker if podman is not available.
ENGINE="${AIIDALAB_MLIP_ENGINE:-}"
if [[ -z "$ENGINE" ]]; then
    if command -v podman &>/dev/null; then
        ENGINE=podman
    elif command -v docker &>/dev/null; then
        ENGINE=docker
    else
        echo "ERROR: neither podman nor docker found." >&2
        exit 1
    fi
fi

echo "=== Building ${TAG} with ${ENGINE} ==="
"${ENGINE}" build \
    -f "${SCRIPT_DIR}/Dockerfile" \
    -t "${TAG}" \
    "${BUILD_ARGS[@]}" \
    "${REPO_ROOT}"

echo
echo "Built ${TAG}"
echo "Run it with:"
if [[ "$ENGINE" == "podman" ]]; then
    echo "  podman run -it --rm -p 8888:8888 --userns=keep-id:uid=1000,gid=100 -v \"\$HOME\":/home/jovyan:Z ${TAG}"
else
    echo "  docker run -it --rm -p 8888:8888 -v \"\$HOME\":/home/jovyan ${TAG}"
fi
echo "or use ./containers/startup.sh"
