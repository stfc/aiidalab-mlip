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

For detailed instructions on running and developing the application locally via Docker/Podman or `aiidalab-launch`, see the [Containers Guide](containers/README.md).

### Guidance
- For running locally via Docker/Podman: see [containers/README.md](containers/README.md).
- For advice on using Aiidalab (including Docker): https://aiidalab.readthedocs.io/en/latest/usage/access/index.html and https://stfc.github.io/alc-ux/user_docs/index.html
- For advice on using Aiida-MLIP (Including `uv` virtual environment): https://stfc.github.io/aiida-mlip/developer_guide/index.html

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
