# Local Docker Registry

## Create Password

```bash
# create password
mkdir /home/johnny/auth

docker run \
  --entrypoint htpasswd \
  httpd:2 -Bbn mlrun mlpass > auth/htpasswd
```

## Create Namespace

```bash
# Create a namespace for MLRun
sudo kubectl create namespace mlrun
```

## Create Secrets

```bash
# Create the Kubernetes secret for authentication from the htpasswd file
sudo kubectl create secret generic registry-auth \
  --from-file=htpasswd=/home/johnny/auth/htpasswd \
  -n mlrun
```

## Deploy Registry

```bash
# create the registry deployment
sudo kubectl apply -f 03_registry.yaml

# validate the deployment
sudo kubectl get pods -n mlrun
sudo kubectl get svc -n mlrun

# Check logs if needed
sudo kubectl logs -n mlrun -l app=registry

# host test
curl -k http://dragon:30500/v2/ -u mlrun:mlpass
```

### Test Pod

```bash
sudo kubectl run -n mlrun test-shell \
  --rm -it --restart=Never \
  --image=alpine:3.19 \
  --command -- sh
```

Inside the pod:

```bash
apk add --no-cache curl
curl http://registry-service.mlrun.svc.cluster.local/v2/ -u mlrun:mlpass
```

## Worth a try

source: https://github.com/yonishelach/nvidia-data-flywheel/blob/78d08369ecbb6a6772444cae65d5a7c51160e227/scripts/mlrun.sh#L43

```bash
sudo kubectl create configmap registry-config \
    --namespace=mlrun \
    --from-literal=insecure_pull_registry_mode=enabled \
    --from-literal=insecure_push_registry_mode=enabled
```

Hack...

```bash
# Set the correct variable on the chief
sudo kubectl -n mlrun set env deployment/mlrun-api-chief \
  MLRUN_HTTPDB__BUILDER__INSECURE_PULL_REGISTRY_MODE=enabled \
  MLRUN_HTTPDB__BUILDER__INSECURE_PUSH_REGISTRY_MODE=enabled

# Set the correct variable on the worker
sudo kubectl -n mlrun set env deployment/mlrun-api-worker \
  MLRUN_HTTPDB__BUILDER__INSECURE_PULL_REGISTRY_MODE=enabled \
  MLRUN_HTTPDB__BUILDER__INSECURE_PUSH_REGISTRY_MODE=enabled


sudo tee /etc/rancher/k3s/registries.yaml > /dev/null <<EOF
mirrors:
  "registry-service.mlrun.svc.cluster.local":
    endpoint:
      - "http://registry-service.mlrun.svc.cluster.local"
EOF

sudo systemctl restart k3s
```

## Local Images

```bash
``bash
docker pull mlrun/mlrun-gpu:1.9.1-py39
docker tag mlrun/mlrun-gpu:1.9.1-py39 dragon:30500/mlrun/mlrun-gpu:1.9.1-py39
docker push dragon:30500/mlrun/mlrun-gpu:1.9.1-py39
docker rmi mlrun/mlrun-gpu:1.9.1-py39
docker rmi dragon:30500/mlrun/mlrun-gpu:1.9.1-py39

# verify push
curl http://dragon:30500/v2/_catalog -u mlrun:mlpass
curl http://dragon:30500/v2/mlrun/mlrun-gpu/tags/list -u mlrun:mlpass
```