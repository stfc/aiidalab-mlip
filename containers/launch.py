#!/usr/bin/env python3
"""Automated launcher for aiidalab-mlip using the official aiidalab-launch tool.

It configures the AiiDAlab profile with correct mount paths, starts the
container, installs the editable packages, and configures AiiDA.

Sibling dependencies (aiida-mlip, alc-aiidalab-widgets) are by default
installed from their GitHub ``main`` branches. Set the environment variable
``AIIDALAB_MLIP_DEV=1`` to switch to development mode: sibling directories
``../aiida-mlip`` (or ``../stfc_aiida-mlip``) and ``../alc-aiidalab-widgets``
are then bind-mounted into the container and editable-installed, giving a live
edit loop for co-development.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import click
import toml

# GitHub URLs for the sibling dependencies (used in default / non-dev mode).
_MLIP_GIT_URL = "git+https://github.com/stfc/aiida-mlip.git"
_WIDGETS_GIT_URL = "git+https://github.com/stfc/alc-aiidalab-widgets.git@add-parameters"


def detect_runtime(container_name: str) -> str:
    """Return 'podman' or 'docker' depending on which runtime owns the container.

    ``aiidalab-launch`` itself manages the container, but we still need to talk
    to a container runtime directly for a few host-side tasks (editable pip
    install as root, REST API proxy).
    """
    for runtime in ("podman", "docker"):
        proc = subprocess.run(
            [runtime, "inspect", container_name],
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0:
            return runtime
    print(
        f"ERROR: could not find container '{container_name}' under podman or docker. "
        "Is the AiiDAlab instance running?"
    )
    sys.exit(1)


def main():
    """Configure, start, and initialize the AiiDAlab Launch container."""
    script_dir = Path(__file__).resolve().parent
    repo_dir = script_dir.parent
    workspace_root = repo_dir.parent

    # Dev mode: bind-mount local sibling repos and editable-install them.
    # Default (no env var, or AIIDALAB_MLIP_DEV=0): install siblings from GitHub.
    dev_mode = os.environ.get("AIIDALAB_MLIP_DEV", "").strip() in ("1", "true", "True")

    mlip_dir = workspace_root / "aiida-mlip"
    if not mlip_dir.is_dir():
        mlip_dir = workspace_root / "stfc_aiida-mlip"

    widgets_dir = workspace_root / "alc-aiidalab-widgets"

    if dev_mode:
        if not mlip_dir.is_dir():
            print(f"ERROR: AIIDALAB_MLIP_DEV=1 but sibling directory 'aiida-mlip' "
                  f"not found at {mlip_dir}")
            sys.exit(1)
        if not widgets_dir.is_dir():
            print(f"ERROR: AIIDALAB_MLIP_DEV=1 but sibling directory 'alc-aiidalab-widgets' "
                  f"not found at {widgets_dir}")
            sys.exit(1)
        print("=== Dev mode: local sibling repos will be bind-mounted + editable-installed ===")
    else:
        print("=== Sibling dependencies will be installed from GitHub (main) ===")

    # 1. Locate and load config.toml
    config_dir = Path(click.get_app_dir("org.aiidalab.aiidalab_launch"))
    config_path = config_dir / "config.toml"

    if config_path.is_file():
        config = toml.load(config_path)
    else:
        config = {"default_profile": "default", "version": "2024.1020", "profiles": {}}

    if "profiles" not in config:
        config["profiles"] = {}

    # 2. Configure or create 'aiidalab-mlip' profile
    profile_name = "aiidalab-mlip"
    if profile_name not in config["profiles"]:
        print(f"Adding new profile '{profile_name}' to AiiDAlab Launch config...")
        # Determine non-conflicting port
        ports = [p.get("port", 8888) for p in config["profiles"].values()]
        port = max(ports) + 1 if ports else 8889
        config["profiles"][profile_name] = {
            "port": port,
            "default_apps": [],
            "system_user": "jovyan",
            "home_mount": f"aiidalab_{profile_name}_home",
        }

    profile = config["profiles"][profile_name]
    profile["image"] = "ghcr.io/stfc/alc-ux/base:py310"

    # Set up bind mounts. The app itself is ALWAYS bind-mounted (it must be
    # at /home/jovyan/apps/aiidalab-mlip for AiiDAlab app discovery and is
    # editable-installed).
    extra_mounts = [f"{repo_dir}:/home/jovyan/apps/aiidalab-mlip:rw"]
    if dev_mode:
        extra_mounts.append(f"{mlip_dir}:/tmp/src/aiida-mlip:rw")
        extra_mounts.append(f"{widgets_dir}:/tmp/src/alc-aiidalab-widgets:rw")
    profile["extra_mounts"] = extra_mounts

    # Save config
    config_dir.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as fh:
        toml.dump(config, fh)
    print(f"Configured profile '{profile_name}' at {config_path}")

    # 3. Start the container
    print(f"\n=== Starting AiiDAlab instance '{profile_name}' ===")
    subprocess.run(
        ["aiidalab-launch", "start", "-p", profile_name, "--restart", "--no-browser"],
        check=True,
    )

    container_name = f"aiidalab_{profile_name}"
    runtime = detect_runtime(container_name)

    # Make any pre-existing checkpoint directories world-writable
    chmod_paths = ["/home/jovyan/apps/aiidalab-mlip"]
    if dev_mode:
        chmod_paths.append("/tmp/src/aiida-mlip")
        chmod_paths.append("/tmp/src/alc-aiidalab-widgets")
    subprocess.run([
        runtime, "exec", "--user", "root", container_name,
        "find", *chmod_paths,
        "-name", ".ipynb_checkpoints", "-type", "d",
        "-exec", "chmod", "777", "{}", "+",
    ], check=False)

    # 4. Install dependencies inside the container.
    print("\n=== Installing packages inside the container (as root) ===")
    sibling_targets = []
    if dev_mode:
        print("  Dev mode: editable-installing siblings from bind-mounts")
        sibling_targets = ["-e", "/tmp/src/aiida-mlip",
                           "-e", "/tmp/src/alc-aiidalab-widgets"]
    else:
        print("  Installing siblings from GitHub main")
        sibling_targets = [_MLIP_GIT_URL, _WIDGETS_GIT_URL]

    # Ensure pip constraints do not block aiida-core upgrade for aiida-mlip (~=2.7.4)
    subprocess.run([
        runtime, "exec", "--user", "root", container_name,
        "sed", "-i", "/aiida-core/d", "/opt/requirements.txt",
    ], check=False)

    install_cmd = [
        runtime,
        "exec",
        "--user",
        "root",
        container_name,
        "pip",
        "install",
        "--pre",
        "--no-cache-dir",
        "--no-user",
        *sibling_targets,
        "janus-core[mace]",
        "backports.tarfile",
        "-e", "/home/jovyan/apps/aiidalab-mlip",
    ]
    subprocess.run(install_cmd, check=True)

    # Patch layouts.py to include future annotations if needed
    subprocess.run([
        runtime, "exec", "--user", "root", container_name,
        "bash", "-c",
        "F=$(find /opt/conda -name 'layouts.py' -path '*/alc_aiidalab_widgets/*') && "
        "[ -n \"$F\" ] && ! grep -q 'from __future__ import annotations' \"$F\" && "
        "sed -i '1s|^|from __future__ import annotations\\n|' \"$F\" || true; "
        "jupyter serverextension disable --sys-prefix jupyter_lsp || true"
    ], check=False)

    # Restart AiiDA daemon to load newly installed plugins
    print("\n=== Restarting AiiDA daemon to load freshly installed plugins ===")
    subprocess.run([
        runtime, "exec", container_name,
        "verdi", "daemon", "restart",
    ], check=False)

    # 5. Start the AiiDA REST API
    print("\n=== Starting AiiDA REST API inside the container ===")
    subprocess.run([
        "aiidalab-launch", "exec", "-p", profile_name, "--",
        "bash", "/home/jovyan/apps/aiidalab-mlip/containers/start_restapi.sh"
    ], check=True)

    # 6. Expose the REST API on a host port via a proxy container.
    print("\n=== Exposing AiiDA REST API on host port 5050 ===")
    proxy_name = "aiidalab-mlip-restapi-proxy"
    proxy_network = "aiidalab-mlip-net"

    subprocess.run(
        [runtime, "network", "create", proxy_network],
        check=False,
        stdout=subprocess.DEVNULL,
    )
    subprocess.run(
        [runtime, "network", "connect", proxy_network, container_name],
        check=False,
    )
    subprocess.run([runtime, "rm", "-f", proxy_name], check=False)
    subprocess.run([
        runtime,
        "run",
        "-d",
        "--name",
        proxy_name,
        "--network",
        proxy_network,
        "-p",
        "5050:5000",
        "alpine/socat",
        "TCP-LISTEN:5000,fork",
        f"TCP:{container_name}:5000",
    ], check=True)

    # 7. Configure AiiDA (localhost computer, codes, and daemon)
    print("\n=== Running AiiDA configuration inside the container ===")
    setup_cmd = [
        "aiidalab-launch",
        "exec",
        "-p",
        profile_name,
        "--",
        "bash",
        "/home/jovyan/apps/aiidalab-mlip/containers/setup-aiida.sh",
    ]
    subprocess.run(setup_cmd, check=True)

    # 8. Retrieve URL
    try:
        print("\n=== Retrieving clickable URLs ===")
        status_proc = subprocess.run(
            ["aiidalab-launch", "status"],
            capture_output=True,
            text=True,
            check=False,
        )
        if status_proc.returncode == 0:
            url = None
            for line in status_proc.stdout.splitlines():
                if "aiidalab-mlip" in line and "http://" in line:
                    for part in line.split():
                        if part.startswith("http://") or part.startswith("https://"):
                            url = part
                            break
                    if url:
                        break

            if url:
                token = ""
                if "token=" in url:
                    token = url.split("?")[-1]

                app_url = f"http://localhost:{profile['port']}/apps/apps/aiidalab-mlip/main.ipynb"
                lab_url = f"http://localhost:{profile['port']}/lab/tree/apps/aiidalab-mlip/main.ipynb"
                if token:
                    app_url = f"{app_url}?{token}"
                    lab_url = f"{lab_url}?{token}"

                print("=================================================================")
                print("  AiiDAlab is ready! Click one of the links below to open:     ")
                print("")
                print("  1. Direct App Mode (Recommended):")
                print("     " + app_url)
                print("")
                print("  2. JupyterLab Editor Mode (to view/edit code):")
                print("     " + lab_url)
                print("=================================================================")
            else:
                print("AiiDAlab is running. Run 'aiidalab-launch status' to find the URL.")
        else:
            print("AiiDAlab is running. Run 'aiidalab-launch status' to find the URL.")
    except Exception as e:
        print(f"Note: Could not retrieve URL automatically: {e}")


if __name__ == "__main__":
    main()
