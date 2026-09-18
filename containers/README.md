# AiiDAlab MLIP Containers

This directory contains tooling for running `aiidalab-mlip` inside an AiiDAlab
container, covering two complementary workflows:

1. **Live development** — the automated `aiidalab-launch` script
   ([`launch.py`](launch.py)) that mounts your local checkouts and gives an
   instant edit→refresh loop inside a running AiiDAlab container.
2. **Deployment** — a standard, self-contained Docker/Podman image
   ([`Dockerfile`](Dockerfile)) with the app and its dependencies baked in,
   plus a startup script for launching it on a user's machine.

---

## 1. Live Development (aiidalab-launch)

The launcher uses the official EPFL [AiiDAlab Launch](https://github.com/aiidalab/aiidalab-launch)
tool. We start a standardized AiiDAlab base container (`ghcr.io/stfc/alc-ux/base:py310`),
mount the local packages as live bind-mounts, and install them in editable mode
inside.

- **Zero build times:** no waiting for custom Docker/Podman images to compile.
- **True live editing:** changes to the local `aiidalab-mlip`, `aiida-mlip`
  and `alc-aiidalab-widgets` checkouts are instantly active in the container.
- **Mac / Podman friendly:** `aiidalab-launch` handles Podman VM socket
  configuration and port forwarding out of the box.

### Required layout for dev mode

The launcher optionally supports sibling directories for co-development:

```text
<workspace>
├── aiidalab-mlip          # this repository
├── aiida-mlip             # local dependency (optional)
└── alc-aiidalab-widgets   # local dependency (optional)
```

### Quick start

```bash
pipx install aiidalab-launch
python3 containers/launch.py
```

The script autonomously configures an `aiidalab-mlip` profile, bind-mounts the
local directory, starts the container (Podman/Docker), editable-installs the
packages, configures AiiDA inside the container, and prints direct clickable
URLs:

1. **Direct App Mode (Recommended):**
   `http://localhost:8889/apps/apps/aiidalab-mlip/main.ipynb?token=...`
2. **JupyterLab Editor Mode:**
   `http://localhost:8889/lab/tree/apps/aiidalab-mlip/main.ipynb?token=...`

Set `AIIDALAB_MLIP_DEV=1` to also bind-mount and editable-install the two
sibling repositories for co-development. Without it, siblings are installed
from their `main` GitHub branches.

Development commands:

```bash
aiidalab-launch logs -p aiidalab-mlip
aiidalab-launch status -p aiidalab-mlip
aiidalab-launch stop -p aiidalab-mlip
aiidalab-launch exec -p aiidalab-mlip -- <command>
```

---

## 2. Deployment Image

For production/end-user deployment we build a standard container image with the
app baked in, following the ALC-UX
[docker image guide](https://stfc.github.io/alc-ux/). The image is based on
`ghcr.io/stfc/alc-ux/base:py310` (a Python 3.10 port of the official
`aiidalab/full-stack` image).

The image:

- installs `aiida-mlip`, `alc-aiidalab-widgets`, and `janus-core[mace]`;
- copies this repository into `/opt/aiidalab-mlip/app` and `pip install`s the
  `aiidalab-mlip` package;
- registers a `before-notebook.d` hook that links the app into
  `<home>/apps/aiidalab-mlip` and configures AiiDA on first boot — registering
  the localhost `janus` and `python3` codes and starting the AiiDA REST API.

### Build

Using the build script (defaults to `podman`, falls back to `docker`):

```bash
./containers/build.sh                       # tags aiidalab-mlip:latest
./containers/build.sh --tag aiidalab-mlip:0.1.0
```

or directly:

```bash
podman build -f containers/Dockerfile -t aiidalab-mlip:latest .
```

### Run

#### Method A: Using the Startup Script (Recommended)

The startup script handles user namespaces, volume permissions, profile setup, and GPU flags automatically:

```bash
# CPU mode with data persistence in $HOME
./containers/startup.sh

# GPU mode
./containers/startup.sh --gpu

# Custom bind directory and port
./containers/startup.sh --bind /path/to/my_data --port 9999 --gpu
```

---

#### Method B: Running Directly with Podman

##### 1. Mounting a local working directory in Linux (CCP5 approach)

Following the [CCP5 Summer School Linux guidelines](https://summer.ccp5.ac.uk/introduction.html#run-locally), to share a local folder with the container without encountering permission errors in rootless Podman:

```bash
# Create a local workspace directory
mkdir -p work

# Set ownership to container user (jovyan uid 1000, gid 100) inside the Podman user namespace
podman unshare chown 1000:100 work

# Run with the folder mounted at /home/jovyan/work
podman run -it --rm \
    --security-opt seccomp=unconfined \
    -p 8888:8888 \
    -v ./work:/home/jovyan/work:Z \
    aiidalab-mlip:latest
```

##### 2. Mounting your entire `$HOME` directory

If mounting your full home directory for complete persistence, use `--userns=keep-id` to map your host user to container UID 1000 (`jovyan`):

```bash
podman run -it --rm \
    --security-opt seccomp=unconfined \
    -p 8888:8888 \
    --userns=keep-id:uid=1000,gid=100 \
    -v "$HOME":/home/jovyan:Z \
    aiidalab-mlip:latest
```

---

### GPU Acceleration (NVIDIA)

`aiidalab-mlip` and `janus-core` support GPU acceleration for MLIP models (e.g. MACE, SevenNet, CHGNet) via PyTorch and CUDA.

#### Prerequisites on the Host

1. Ensure the NVIDIA proprietary driver is installed and working (`nvidia-smi`).
2. Ensure [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) is installed.
3. For Podman, generate the Container Device Interface (CDI) specification once:
   ```bash
   sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml
   # Verify CDI detects your GPU:
   nvidia-ctk cdi list
   ```

#### Running with GPU

- **With Podman (CDI)**:
  ```bash
  podman run -it --rm \
      --security-opt seccomp=unconfined \
      --device nvidia.com/gpu=all \
      --userns=keep-id:uid=1000,gid=100 \
      -p 8888:8888 \
      -v "$HOME":/home/jovyan:Z \
      aiidalab-mlip:latest
  ```

- **With Docker**:
  ```bash
  docker run -it --rm \
      --gpus all \
      -p 8888:8888 \
      -v "$HOME":/home/jovyan \
      aiidalab-mlip:latest
  ```

- **With Apptainer / Singularity**:
  ```bash
  apptainer run --nv \
      --compat --cleanenv \
      --home /home/jovyan \
      --bind "$HOME":/home/jovyan \
      docker://aiidalab-mlip:latest
  ```

- **With `startup.sh`**:
  ```bash
  ./containers/startup.sh --gpu
  ```

#### Verifying GPU inside the Container

To check whether CUDA is accessible to PyTorch in the running container:

```bash
podman run --rm --device nvidia.com/gpu=all aiidalab-mlip:latest \
    python3 -c "import torch; print('CUDA Available:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
```

When running calculations inside the `aiidalab-mlip` app, select **`cuda`** as the device in the code settings step to execute simulations on the GPU.

---

### First-boot AiiDA profile

The base image creates a default AiiDA profile on first start using these
environment variables:

| Variable                     | Default          |
| ---------------------------- | ---------------- |
| `AIIDA_PROFILE_NAME`         | `default`        |
| `AIIDA_USER_EMAIL`           | `aiida@localhost` |
| `AIIDA_USER_FIRST_NAME`      | `Giuseppe`       |
| `AIIDA_USER_LAST_NAME`       | `Verdi`          |
| `AIIDA_USER_INSTITUTION`     | `Khedivial`      |

Set `SETUP_DEFAULT_AIIDA_PROFILE=false` to skip profile creation (e.g. when
reusing an existing profile from a previous bind mount).

### Registered AiiDA Codes

On container startup, the following codes are automatically configured on the
`localhost` computer:

- `janus@localhost`: Points to the `janus` command line interface from `janus-core`.
- `python3@localhost`: Points to the container's Python executable.

