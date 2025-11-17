# Local Docker Registry

```bash
# really need to fix this so I don't have to keep doing it
sudo chmod 644 /etc/rancher/k3s/k3s.yaml
```

## Create Password

```bash
# create password
mkdir /home/johnny/auth

docker run \
  --entrypoint htpasswd \
  httpd:2 -Bbn mlrun mlpass > auth/htpasswd
```

## Create Namespace

Create a namespace for MLRun.

```bash
sudo kubectl create namespace mlrun
```

## Create Secrets

Create the Kubernetes secret for authentication from the htpasswd file.

```bash
kubectl create secret generic registry-auth \
  --from-file=htpasswd=/home/johnny/auth/htpasswd \
  -n mlrun
```

## Deploy Registry

```bash
# create the registry deployment
kubectl apply -f 03_registry.yaml

# validate the deployment
kubectl get pods -n mlrun
kubectl get svc -n mlrun

# Check logs if needed
kubectl logs -n mlrun -l app=registry

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

## Set Registry

```bash
sudo tee /etc/rancher/k3s/registries.yaml > /dev/null <<EOF
mirrors:
  "registry-service.mlrun.svc.cluster.local":
    endpoint:
      - "http://dragon:30500"
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