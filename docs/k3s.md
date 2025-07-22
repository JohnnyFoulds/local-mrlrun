# K3s Deployment

For local testing a Lightweight Kubernetes cluster is used. [K3s](https://k3s.io/) is a lightweight Kubernetes distribution that is easy to install and manage. It is designed for resource-constrained environments and is ideal for local development and testing.

## Install K3s

```bash
curl -sfL https://get.k3s.io | sh - 
# Check for Ready node, takes ~30 seconds 
sudo k3s kubectl get node 
```

## Install MLRun

The installation follows the [How to Install MLRun Kit Using Kubernetes](https://www.youtube.com/watch?v=Z6mTw7_n8iE) guide.

### Pre-requisites

Please note that a requirement is an accessible docker-registry (such as [Docker Hub](https://docs.docker.com/accounts/create-account/)). The registry's URL and credentials are consumed by the applications via a pre-created secret.

#### Helm

Helm >=3.6 CLI is required to install MLRun. If you don't have it installed, you can do so with the following command:

```bash
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh
```


### Test Kubernetes

```bash
sudo kubectl get nodes
```

### Install MLRun

```bash
# Create a namespace for MLRun
sudo kubectl create namespace mlrun

#Add the helm chart repo
sudo helm repo add mlrun-ce https://mlrun.github.io/ce
sudo helm repo list
sudo helm repo update
```

```bash
# Create a secret for docker-registry
# sudo kubectl --namespace mlrun create secret docker-registry registry-credentials \
#     --docker-server https://registry.hub.docker.com/ \
#     --docker-username shambi \
#     --docker-password 'Sh!tB@llz' \
#     --docker-email hfoulds@gmail.com

# log into docker locally
docker login -u shambi

# create a new secret
sudo kubectl --namespace mlrun create secret docker-registry registry-credentials \
    --from-file=/home/johnny/.docker/config.json

# validate the secret
sudo kubectl get secrets -n mlrun
```

To install the chart with the release name `mlrun-ce` use the following command.
> `global.externalHostAddress` is the IP address of the host machine.

```bash
sudo helm --namespace mlrun \
    --kubeconfig /etc/rancher/k3s/k3s.yaml \
    install mlrun-ce \
    --wait \
    --timeout 12960s \
    --set global.registry.url=index.docker.io/shambi \
    --set global.registry.secretName=registry-credentials \
    --set global.externalHostAddress=192.168.1.184 \
    --set nuclio.dashboard.externalIPAddresses=192.168.1.184 \
    mlrun-ce/mlrun-ce
```

In a separate terminal progress can be viewed with the following command:

```bash
sudo kubectl get pods -n mlrun -w
``` 

### Error

If something goes wrong, you can delete the namespace and start over.

```bash
sudo kubectl delete namespace mlrun

# extreme measure
sudo systemctl stop k3s
sudo systemctl start k3s
```

## Results

```
NAME: mlrun-ce
LAST DEPLOYED: Wed May 21 12:49:38 2025
NAMESPACE: mlrun
STATUS: deployed
REVISION: 1
NOTES:
You're up and running!

Jupyter UI is available at:
192.168.1.184:30040

Nuclio UI is available at:
192.168.1.184:30050

MLRun UI is available at:
192.168.1.184:30060

MLRun API is available at:
192.168.1.184:30070

Minio UI is available at:
192.168.1.184:30090
-  username: minio
-  password: minio123

Minio API is available at:
192.168.1.184:30080

Pipelines UI is available at:
192.168.1.184:30100

Grafana UI is available at:
192.168.1.184:30010

Prometheus UI is available at:
192.168.1.184:30020

Happy MLOPSing!!! :]
```

## NVIDIA Container Runtime

### 1. Install the nvidia-container package repository 

```bash
# Configure the production repository
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Update the packages list from the repository
sudo apt-get update

# Install the NVIDIA Container Toolkit packages
export NVIDIA_CONTAINER_TOOLKIT_VERSION=1.17.8-1
  sudo apt-get install -y \
      nvidia-container-toolkit=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
      nvidia-container-toolkit-base=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
      libnvidia-container-tools=${NVIDIA_CONTAINER_TOOLKIT_VERSION} \
      libnvidia-container1=${NVIDIA_CONTAINER_TOOLKIT_VERSION}

# look at existing packages
#sudo apt-cache search nvidia | grep -P '^nvidia-(driver-)?[0-9]+\s'
#sudo apt-cache search cuda-drivers-fabricmanager

# Install the nvidia container runtime packages
sudo apt install -y nvidia-container-runtime cuda-drivers-fabricmanager-550

# restart the k3s service
sudo systemctl restart k3s

# Confirm that the nvidia container runtime has been found by k3s
sudo grep nvidia /var/lib/rancher/k3s/agent/etc/containerd/config.toml
```