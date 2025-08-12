# local-mrlrun
Experiment with code Sharing between teams who might not have an MLRun deployment

## Local Environment

```bash
# Create a virtual environment
make venv

# Activate the virtual environment
conda activate local-mlrun
```

If you want to remove the vitual environment you can run `make clean`.

## MLRun Docker Setup

### Get Deployment Script

```bash
curl https://raw.githubusercontent.com/mlrun/mlrun-setup/development/mlsetup.py > mlsetup.py
pip install click~=8.0.0 python-dotenv~=0.17.0
```

### Run Deployment Script

```bash
python mlsetup.py docker 
```

You may need to execute the following if you are using a recent version of the docker compose plugin:

```bash
echo -e '#!/bin/sh\nexec docker compose "$@"' | sudo tee /usr/local/bin/docker-compose > /dev/null && sudo chmod +x /usr/local/bin/docker-compose
```