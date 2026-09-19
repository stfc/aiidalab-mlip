# AiiDAlab-MLIP

Interactive web interface for running Machine Learning Interatomic Potential (MLIP) calculations using [AiiDA](https://www.aiida.net/) and [aiida-mlip](https://github.com/stfc/aiida-mlip).

This app is under active development. Current supported calculations are Singlepoint and Geometry Optimization.

## Features

- **Structure Upload**: Load materials from CIF, XYZ, or other structure files.
- **Pre-trained Models**: Use MACE-MP-0 models trained on Materials Project.
- **Singlepoint Calculations**: Compute energy, forces, and stress tensors.
- **Geometry Optimization**: Relax structures to local minima.
- **Molecular dynamics**: molecular dynamics
- **Interactive Results**: View outputs and process metadata.
- **Automatic Provenance**: Full workflow tracking with AiiDA.

## Quick Start

Run the container using Podman and open `http://localhost:8888`:

```bash
podman run -it --rm -p 8888:8888 ghcr.io/stfc/aiidalab-mlip:amd64-latest
```

Alternatively, use the provided startup script (which handles permissions, volume persistence, and profile setup automatically):

```bash
./containers/startup.sh --image ghcr.io/stfc/aiidalab-mlip:amd64-latest
```

For detailed instructions on running and developing the application locally via Docker/Podman or `aiidalab-launch`, see the [Containers Guide](containers/README.md).

### Guidance
- For running locally via Docker/Podman: see [containers/README.md](containers/README.md).
- For advice on using Aiidalab (including Docker): https://aiidalab.readthedocs.io/en/latest/usage/access/index.html and https://stfc.github.io/alc-ux/user_docs/index.html
- For advice on using Aiida-MLIP (Including `uv` virtual environment): https://stfc.github.io/aiida-mlip/developer_guide/index.html

## License

BSD 3-Clause License

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

Contributors to this project were funded by

[![PSDI](https://raw.githubusercontent.com/stfc/aiida-mlip/main/docs/source/images/psdi-100.webp)](https://www.psdi.ac.uk/)
[<img src="https://raw.githubusercontent.com/stfc/aiida-mlip/main/docs/source/images/alc.svg" width="200" height="100" alt="ALC" />](https://adalovelacecentre.ac.uk/)
[![CoSeC](https://raw.githubusercontent.com/stfc/aiida-mlip/main/docs/source/images/cosec-100.webp)](https://www.scd.stfc.ac.uk/Pages/CoSeC.aspx)
