# NVIDIA Container Runtime

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
#?? maybe ?? kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.13.0/nvidia-device-plugin.yml

# Docker Debugging [B]
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

sudo docker run --rm --gpus all nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04 nvidia-smi

# containerd Debugging [C]
sudo ctr image pull docker.io/nvidia/cuda:12.4.1-base-ubuntu22.04

sudo ctr run --rm -t \
  --runc-binary=/usr/bin/nvidia-container-runtime \
  --env NVIDIA_VISIBLE_DEVICES=all \
  docker.io/nvidia/cuda:12.4.1-base-ubuntu22.04 \
  cuda-12.4.1-base-ubuntu22.04 nvidia-smi

# Add the NVIDIA Helm repository. [D]
helm repo add nvidia https://nvidia.github.io/gpu-operator

# Update the repository
helm repo update

# Install GPU operator
helm install --wait --generate-name nvidia/gpu-operator

# Verify the deployment
kubectl get pods | grep nvidia
#watch -t 'kubectl get pods | grep nvidia'

kubectl get nodes "-o=custom-columns=NAME:.metadata.name,GPU:.status.allocatable.nvidia\.com/gpu"
```

## Additional Containerd Configuration

```bash
sudo cp /var/lib/rancher/k3s/agent/etc/containerd/config.toml /var/lib/rancher/k3s/agent/etc/containerd/config.toml.tmpl

# Add the NVIDIA runtime to the containerd configuration
sudo tee -a /var/lib/rancher/k3s/agent/etc/containerd/config.toml.tmpl > /dev/null <<'EOF'

[plugins."io.containerd.cri.v1.runtime".containerd]
  default_runtime_name = "nvidia"
EOF

# show the changes
sudo cat /var/lib/rancher/k3s/agent/etc/containerd/config.toml.tmpl

sudo systemctl restart k3s

sudo grep "default_runtime_name" /var/lib/rancher/k3s/agent/etc/containerd/config.toml
```