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
curl http://registry-service.mlrun.svc.cluster.local:5000/v2/ -u mlrun:mlpass
```

## Worth a try

source: https://github.com/yonishelach/nvidia-data-flywheel/blob/78d08369ecbb6a6772444cae65d5a7c51160e227/scripts/mlrun.sh#L43

```bash
  kubectl create configmap registry-config \
    --namespace=mlrun \
    --from-literal=insecure_pull_registry_mode=enabled \
    --from-literal=insecure_push_registry_mode=enabled
```

# Local Imags

```bash
``bash
docker pull mlrun/mlrun-gpu:1.9.1-py39
docker tag mlrun/mlrun-gpu:1.9.1-py39 dragon:30500/mlrun/mlrun-gpu:1.9.1-py39
docker push dragon:30500/mlrun/mlrun-gpu:1.9.1-py39
docker rmi mlrun/mlrun-gpu:1.9.1-py39
docker rmi dragon:30500/mlrun/mlrun-gpu:1.9.1-py39

# verify push
curl http://dragon:6500/v2/_catalog
curl http://dragon:6500/v2/mlrun/mlrun-gpu/tags/list
```
```