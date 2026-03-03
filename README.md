# AiiDAlab-MLIP

Interactive web interface for running Machine Learning Interatomic Potential (MLIP) calculations using [AiiDA](https://www.aiida.net/) and [aiida-mlip](https://github.com/stfc/aiida-mlip).

## Features

-  **Structure Upload**: Load materials from CIF, XYZ, or other structure files
-  **Pre-trained Models**: Use MACE-MP-0 models trained on Materials Project
-  **Singlepoint Calculations**: Compute energy, forces, and stress tensors
-  **Interactive Results**: View results with 3D structure visualization
-  **Automatic Provenance**: Full workflow tracking with AiiDA

## Installation

### Option 1: Docker (Recommended for Development)

**Step 1: Start the container**
```bash
# Pull the AiiDAlab base image (Python 3.9 with AiiDA pre-installed)
docker pull aiidalab/full-stack:latest

# Start container with volume mounts
# Replace /path/to with your actual paths!
docker run -d \
  --name aiidalab-mlip \
  -p 8888:8888 \
  -v /path/to/aiidalab-mlip:/home/jovyan/apps/aiidalab-mlip \
  -v /path/to/aiida-mlip:/home/jovyan/aiida-mlip \
  aiidalab/full-stack:latest

# Example with real paths:
# -v /home/jessi/work/aiida/aiidalab-mlip:/home/jovyan/apps/aiidalab-mlip \
# -v /home/jessi/work/aiida/aiida-mlip:/home/jovyan/aiida-mlip \
```

**Step 2: Install dependencies inside the container**
```bash
# Enter the running container
docker exec -it aiidalab-mlip bash

# Now you're inside the container. Run these commands:

# Install PyTorch (CPU version, 186 MB)
pip install torch==2.2.0 --index-url https://download.pytorch.org/whl/cpu

# Install aiida-mlip in editable mode (Python 3.9 compatible branch)
pip install -e /home/jovyan/aiida-mlip

# Install this app in editable mode
pip install -e /home/jovyan/apps/aiidalab-mlip

# Configure janus code
verdi code create core.code.installed \
  --computer=localhost \
  --label=janus \
  --default-calc-job-plugin=core.arithmetic.add \
  --filepath-executable=janus \
  --non-interactive

# Exit the container shell
exit
```

**Step 3: Access the web interface**
```bash
# Get the access token
docker logs aiidalab-mlip 2>&1 | grep "token=" | tail -1

# Open in your browser:
# http://127.0.0.1:8888/?token=<TOKEN>
```

**Persistent setup:** The container persists even after stopping!
```bash
docker stop aiidalab-mlip   # Stop without deleting
docker start aiidalab-mlip  # Restart with all packages intact
```

### Option 2: AiiDAlab Installation (not tested)

This app can be installed directly in AiiDAlab:

```bash
aiidalab install mlip@https://github.com/stfc/aiidalab-mlip
```

## Requirements

- Python 3.9 (for AiiDAlab compatibility)
- [aiida-mlip](https://github.com/stfc/aiida-mlip) - Python 3.9 compatible branch
- PyTorch 2.2.0+
- janus-core
- nglview (for 3D visualization)

## Usage

1. **Upload Structure** (Step 1)
   - Load your material structure from file or example structures
   - Preview the structure before calculations

2. **Select Model** (Step 2)
   - Choose from pre-trained MACE-MP-0 models:
     - **small**: Fast, general purpose
     - **medium**: Balanced accuracy/speed
     - **large**: Highest accuracy

3. **Run Calculation** (Step 3)
   - Select calculation type (Singlepoint, Geometry Optimization, Molecular Dynamics)
   - Configure computational parameters
   - Submit to AiiDA

4. **View Results** (Step 4)
   - Automatically loads results after submission
   - Browse previous calculations from process list
   - Interactive 3D structure visualization
   - View energy, forces, and stress tensors

## Architecture

This app uses the Model-View-Controller pattern:

```
src/aiidalab_mlip/
├── process.py      # Data models (traitlets-based state)
├── structure.py    # Step 1: Structure upload
├── training.py     # Step 2: Model selection
├── prediction.py   # Step 3: Calculation submission
├── results.py      # Step 4: Results visualization
└── main.py         # App entry point and wizard setup
```

See [LEARNING_OUTCOMES.md](LEARNING_OUTCOMES.md) for detailed architecture documentation.

## Development

### Code Changes
It is recommended to use uv for dependancy management (https://stfc.github.io/aiida-mlip/developer_guide/index.html).
Edit files in `src/aiidalab_mlip/` and restart the Jupyter kernel to see changes.

### Running Tests

```bash
uv pip install pytest
pytest tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with clear commit messages
4. Add tests for new functionality
5. Submit a pull request

## Known Issues

- Training workflow is not yet implemented in the web interface
- Use the aiida-mlip Python API for custom model training
- Geometry optimization and MD results viewing planned for future release

## License

MIT

## Contact

- **Repository**: https://github.com/stfc/aiidalab-mlip
- **Issues**: https://github.com/stfc/aiidalab-mlip/issues
- **aiida-mlip**: https://github.com/stfc/aiida-mlip

## Acknowledgements

Built with:
- [AiiDA](https://www.aiida.net/) - Workflow manager
- [AiiDAlab](https://www.materialscloud.org/aiidalab) - Interactive interface
- [aiida-mlip](https://github.com/stfc/aiida-mlip) - MLIP calculations
- [janus-core](https://github.com/stfc/janus-core) - MLIP backend
- [MACE](https://github.com/ACEsuit/mace) - Machine learning models


