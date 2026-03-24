# AiiDAlab-MLIP

Interactive web interface for running Machine Learning Interatomic Potential (MLIP) calculations using [AiiDA](https://www.aiida.net/) and [aiida-mlip](https://github.com/stfc/aiida-mlip).

## Quick Start

### Prerequisites
- Docker or local Python 3.9+ environment with `uv` an
- AiiDA installed with branch compatible with python 3.9 https://github.com/JessieGould/aiida-mlip/tree/python39-compat


### Installation

**Option 1: Docker (Recommended)**

```bash
# Clone the repository
git clone https://github.com/stfc/aiidalab-mlip.git # or https://github.com/JessieGould/aiidalab-mlip 
cd aiidalab-mlip

# Start container with volume mounts
docker run -d \
  --name aiidalab-mlip \
  -p 8888:8888 \
  -v $(pwd):/home/jovyan/apps/aiidalab-mlip \
  -v $(cd ../aiida-mlip && pwd):/home/jovyan/aiida-mlip \
  aiidalab/full-stack:latest

# Enter container and install
docker exec -it aiidalab-mlip bash
pip install torch==2.2.0 --index-url https://download.pytorch.org/whl/cpu
pip install -e /home/jovyan/aiida-mlip
pip install -e /home/jovyan/apps/aiidalab-mlip
exit
```

**Option 2: Local Installation (with existing AiiDA setup)**

```bash
# Create and activate UV venv
uv venv mlip-env
source mlip-env/bin/activate

# Install dependencies
uv pip install torch==2.2.0 --index-url https://download.pytorch.org/whl/cpu
uv pip install -e /path/to/aiida-mlip
uv pip install -e .
```

## Access

Once running, access the web interface at:
```
http://localhost:8888
```

For Docker, get the access token:
```bash
docker logs aiidalab-mlip 2>&1 | grep "token=" | tail -1
```


## License

MIT

## Contact

- **Repository**: https://github.com/stfc/aiidalab-mlip
- **Issues**: https://github.com/stfc/aiidalab-mlip/issues
- **aiida-mlip**: https://github.com/stfc/aiida-mlip

