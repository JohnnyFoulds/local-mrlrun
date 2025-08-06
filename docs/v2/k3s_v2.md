# K3s Deployment

For local testing a Lightweight Kubernetes cluster is used. [K3s](https://k3s.io/) is a lightweight Kubernetes distribution that is easy to install and manage. It is designed for resource-constrained environments and is ideal for local development and testing.

## Install K3s

```bash
curl -sfL https://get.k3s.io | sh - 
# Check for Ready node, takes ~30 seconds 
sudo k3s kubectl get node 
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


# Install the nvidia container runtime packages
sudo apt install -y nvidia-container-runtime cuda-drivers-fabricmanager-550

# restart the k3s service
sudo systemctl restart k3s

# Confirm that the nvidia container runtime has been found by k3s
sudo grep nvidia /var/lib/rancher/k3s/agent/etc/containerd/config.toml

# Deploy Nvidia Device Plugin [A]
sudo kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.13.0/nvidia-device-plugin.yml

# Verify GPU Availability
sudo kubectl get nodes "-o=custom-columns=NAME:.metadata.name,GPU:.status.allocatable.nvidia\.com/gpu"
## above step did not [A]

# Docker Debugging [B]
nvidia-ctk runtime configure --runtime=docker
systemctl restart docker

sudo docker run --rm --gpus all nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04 nvidia-smi

# containerd Debugging [C]
sudo ctr image pull docker.io/nvidia/cuda:12.4.1-base-ubuntu22.04

sudo ctr run --rm -t \
  --runc-binary=/usr/bin/nvidia-container-runtime \
  --env NVIDIA_VISIBLE_DEVICES=all \
  docker.io/nvidia/cuda:12.4.1-base-ubuntu22.04 \
  cuda-12.4.1-base-ubuntu22.04 nvidia-smi

# Add the NVIDIA Helm repository. [D]
sudo helm repo add nvidia https://nvidia.github.io/gpu-operator

# Update the repository
sudo helm repo update

# Install GPU operator
sudo helm install --kubeconfig /etc/rancher/k3s/k3s.yaml --wait --generate-name nvidia/gpu-operator

# Verify the deployment
sudo kubectl get pods | grep nvidia
sudo kubectl get nodes "-o=custom-columns=NAME:.metadata.name,GPU:.status.allocatable.nvidia\.com/gpu"
```

## Local Docker Registry

### Create Certificates

```bash
# Create a directory for the certs
mkdir -p /home/johnny/certs

# Generate the key and certificate
openssl req \
  -newkey rsa:4096 -nodes -sha256 -keyout /home/johnny/certs/domain.key \
  -addext "subjectAltName = DNS:dragon" \
  -x509 -days 365 -out /home/johnny/certs/domain.crt \
  -subj "/C=US/ST=CA/L=PaloAlto/O=IT/CN=dragon"
```

### Deploy Container

```bash
# create password
mkdir auth

docker run \
  --entrypoint htpasswd \
  httpd:2 -Bbn mlrun mlpass > auth/htpasswd

# run the container with TLS enabled
docker run -d -p 6500:5000 --restart=always --name registry \
  -v /home/johnny/swan/opt/registry:/var/lib/registry \
  -v /home/johnny/auth:/auth \
  -v /home/johnny/certs:/certs \
  -e "REGISTRY_AUTH=htpasswd" \
  -e "REGISTRY_AUTH_HTPASSWD_REALM=Registry Realm" \
  -e "REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd" \
  -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/domain.crt \
  -e REGISTRY_HTTP_TLS_KEY=/certs/domain.key \
  registry:3
```

### Make Your Docker Daemon Trust the Certificate

```bash
# Create the dedicated directory for your registry's certificate
sudo mkdir -p /etc/docker/certs.d/dragon:6500

# Copy the public certificate into that directory
sudo cp /home/johnny/certs/domain.crt /etc/docker/certs.d/dragon:6500/ca.crt

# Restart the Docker daemon to load the new certificate
sudo systemctl restart docker

sudo cp /home/johnny/certs/domain.crt /var/lib/rancher/k3s/server/tls/dragon-ca.crt

# Create the registries.yaml file with the correct configuration
sudo tee /etc/rancher/k3s/registries.yaml > /dev/null <<EOF
mirrors:
  "dragon:6500":
    endpoint:
      - "https://dragon:6500"
configs:
  "dragon:6500":
    tls:
      ca_file: "/var/lib/rancher/k3s/server/tls/dragon-ca.crt"
EOF
```

```bash
sudo cp /home/johnny/certs/domain.crt /usr/local/share/ca-certificates/dragon.crt
sudo update-ca-certificates
```

more shit to try
```bash
sudo mkdir -p /etc/docker/certs.d/dragon:6500
sudo cp /home/johnny/certs/domain.crt /etc/docker/certs.d/dragon:6500/ca.crt
sudo systemctl restart docker

# containerd
sudo mkdir -p /etc/containerd/certs.d/dragon:6500
sudo tee /etc/containerd/certs.d/dragon:6500/hosts.toml > /dev/null <<EOF
server = "https://dragon:6500"
[host."https://dragon:6500"]
  capabilities = ["pull", "resolve", "push"]
  ca = "/home/johnny/certs/domain.crt"
EOF

sudo systemctl restart containerd
```

sudo mkdir -p /etc/containerd/certs.d/dragon:6500
sudo tee /etc/containerd/certs.d/dragon:6500/hosts.toml > /dev/null <<EOF
server = "https://dragon:6500"
[host."https://dragon:6500"]
  capabilities = ["pull", "resolve", "push"]
  ca = "/etc/containerd/certs.d/dragon:6500/domain.crt"
EOF

sudo cp /home/johnny/certs/domain.crt /etc/containerd/certs.d/dragon:6500/domain.crt
sudo systemctl restart containerd


### Login to the Registry

```bash
# Log into the registry
docker login -u shambi

docker login -u mlrun dragon:6500
docker login localhost:6500
```

## Install MLRun

### Namespace and Helm

```bash
# Create a namespace for MLRun
sudo kubectl create namespace mlrun

#Add the helm chart repo
sudo helm repo add mlrun-ce https://mlrun.github.io/ce
sudo helm repo list
sudo helm repo update
```

### Registry Secret

```bash
# create a new secret
sudo kubectl --namespace mlrun create secret docker-registry registry-credentials \
    --from-file=/home/johnny/.docker/config.json

# validate the secret
sudo kubectl get secrets -n mlrun
```

### Install MLRun

To install the chart with the release name `mlrun-ce` use the following command.
> `global.externalHostAddress` is the IP address of the host machine.


```bash
sudo helm --namespace mlrun \
    --kubeconfig /etc/rancher/k3s/k3s.yaml \
    install mlrun-ce \
    --set global.registry.url=dragon:6500 \
    --set global.registry.secretName=registry-credentials \
    --set global.externalHostAddress=192.168.1.184 \
    --set nuclio.dashboard.externalIPAddresses=192.168.1.184 \
    mlrun-ce/mlrun-ce
```

In a separate terminal progress can be viewed with the following command:

```bash
sudo kubectl get pods -n mlrun -w
``` 

## Trust Certificates in MLRun

```bash
```