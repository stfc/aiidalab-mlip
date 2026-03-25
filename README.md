# AiiDAlab-MLIP

Interactive web interface for running Machine Learning Interatomic Potential (MLIP) calculations using [AiiDA](https://www.aiida.net/) and [aiida-mlip](https://github.com/stfc/aiida-mlip).

## Quick Start
Currently under development 

### Prerequisites
- Docker and Aiidalab https://aiidalab.readthedocs.io/en/latest/usage/access/index.html 
- Local Python 3.9+ environment with `uv` venv see guidance at https://stfc.github.io/aiida-mlip/developer_guide/index.html 
- AiiDA-MLIP installed from branch compatible with python 3.9 https://github.com/JessieGould/aiida-mlip/tree/python39-compat (for Aiidalab compatibility) 


### Installation

**Docker**

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


## Funding

Contributors to this project were funded by

PSDI ALC CoSeC