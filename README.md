# AiiDAlab-MLIP

Interactive web interface for running Machine Learning Interatomic Potential (MLIP) calculations using [AiiDA](https://www.aiida.net/) and [aiida-mlip](https://github.com/stfc/aiida-mlip).

This app is under active development. Current supported calculations are Singlepoint and Geometry Optimization.

## Features

- **Structure Upload**: Load materials from CIF, XYZ, or other structure files.
- **Pre-trained Models**: Use MACE-MP-0 models trained on Materials Project.
- **Singlepoint Calculations**: Compute energy, forces, and stress tensors.
- **Geometry Optimization**: Relax structures to local minima.
- **Interactive Results**: View outputs and process metadata.
- **Automatic Provenance**: Full workflow tracking with AiiDA.

## Quick Start


### Guidance
- For advice on using Aiidalab (including Docker) https://aiidalab.readthedocs.io/en/latest/usage/access/index.html and https://stfc.github.io/alc-ux/user_docs/index.html 
- For advice on using Aiida-MLIP (Including `uv` virtual environment) https://stfc.github.io/aiida-mlip/developer_guide/index.html 
- Aiidalab currently supports Python 3.9 so a compatable image of Aiida-MLIP can be found at https://github.com/JessieGould/aiida-mlip/tree/python39-compat


### Installation (Docker)

Run these commands on the **host machine**.

```bash
# Clone repositories side by side
git clone https://github.com/stfc/aiidalab-mlip.git
git clone -b python39-compat https://github.com/JessieGould/aiida-mlip.git

cd aiidalab-mlip

# Start container with both repos mounted
docker run -d \
  --name aiidalab-mlip \
  -p 8888:8888 \
  -v "$(pwd)":/home/jovyan/apps/aiidalab-mlip \
  -v "$(cd ../aiida-mlip && pwd)":/home/jovyan/aiida-mlip \
  aiidalab/full-stack:edge
```

Now install dependencies **inside the container**:

```bash
docker exec -it aiidalab-mlip bash

pip install torch==2.2.0 --index-url https://download.pytorch.org/whl/cpu
pip install -e /home/jovyan/aiida-mlip
pip install -e /home/jovyan/apps/aiidalab-mlip

exit
```

### Configure AiiDA Code (Required)

`aiida-mlip` expects a configured code entry called `janus@localhost`.

`config_code.yml` is expected from the `aiida-mlip` repo root. If missing, generate it from the aiida-mlip setup tutorial. 

Run on the **host machine**:

```bash
docker cp ../aiida-mlip/config_code.yml aiidalab-mlip:/tmp/config_code.yml
docker exec aiidalab-mlip verdi code create core.code.installed -n --config /tmp/config_code.yml
docker exec aiidalab-mlip verdi daemon restart
```

Verify setup:

```bash
docker exec aiidalab-mlip verdi status
docker exec aiidalab-mlip verdi code list
docker exec aiidalab-mlip python -c "from aiidalab_mlip.main import MainApp; print('ok')"
```

### Access

Open:

```text
http://localhost:8888
```

Get token if prompted:

```bash
docker logs aiidalab-mlip 2>&1 | grep "token=" | tail -1
```

### Persistent Container Usage

```bash
docker stop aiidalab-mlip
docker start aiidalab-mlip
```

## Troubleshooting

**Error: `Code 'janus@localhost' not found`**

- Re-run code registration:
  `docker exec aiidalab-mlip verdi code create core.code.installed -n --config /tmp/config_code.yml`
- Confirm with:
  `docker exec aiidalab-mlip verdi code list`

**Error: `ModuleNotFoundError: No module named 'aiida_mlip'`**

- Reinstall plugin in container:
  `docker exec aiidalab-mlip pip install -e /home/jovyan/aiida-mlip`
- Restart daemon:
  `docker exec aiidalab-mlip verdi daemon restart`

**GeomOpt exits with status `305` and Janus reports `--write-traj` unknown**

- Ensure your `aiida-mlip` checkout contains the Janus CLI compatibility fix (`--traj` instead of `--write-traj`).

## Architecture

This app uses a wizard-style MVC pattern:

```text
src/aiidalab_mlip/
├── process.py      # Data models (traitlets-based state)
├── structure.py    # Step 1: Structure upload
├── training.py     # Step 2: Model selection
├── prediction.py   # Step 3: Calculation submission
├── results.py      # Step 4: Results visualization
└── main.py         # App entry point and wizard setup
```

## License

MIT

## Contact

- Repository: https://github.com/stfc/aiidalab-mlip
- Issues: https://github.com/stfc/aiidalab-mlip/issues
- aiida-mlip: https://github.com/stfc/aiida-mlip

## Acknowledgements

Built with:

- [AiiDA](https://www.aiida.net/) - Workflow manager
- [AiiDAlab](https://www.materialscloud.org/aiidalab) - Interactive interface
- [aiida-mlip](https://github.com/stfc/aiida-mlip) - MLIP calculations
- [janus-core](https://github.com/stfc/janus-core) - MLIP backend
- [MACE](https://github.com/ACEsuit/mace) - Machine learning models

## Funding

Contributors to this project were funded by PSDI ALC CoSeC.