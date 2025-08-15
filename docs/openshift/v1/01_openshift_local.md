# OpenShift Local

## Prerequisites

```bash
# Update package list
sudo apt update

# Install KVM and libvirt
sudo apt install qemu-kvm libvirt-daemon libvirt-daemon-system

# Verify KVM installation
kvm-ok

# Install QEMU and virtiofsd
sudo apt install qemu-system virtiofsd

# Add your user to the libvirt group
sudo usermod -aG libvirt $USER
newgrp libvirt
```

## Download

```bash
wget https://developers.redhat.com/content-gateway/rest/mirror/pub/openshift-v4/clients/crc/latest/crc-linux-amd64.tar.xz

# download the pull-secret.txt (from the https://console.redhat.com/openshift/create/local)
```

## Run initial setup

```bash
# extract installation files
tar -xvf crc-linux-amd64.tar.xz
cd crc-linux-2.53.0-amd64

# Move binary to your PATH
sudo mv crc-linux-*/crc /usr/local/bin/

# Make it executable
sudo chmod +x /usr/local/bin/crc

# had to add these because of installation problem: https://github.com/crc-org/crc/issues/4370
crc config set network-mode user
crc cleanup

# start the setup - you will be asked to log in and run the command again
# for the libvirt group
crc setup
```

## Create Minmal OpenShift 4 Cluster

This will require the pull secret to be entered.

```bash
# stop k3s if it is already running
sudo systemctl stop k3s
sudo /usr/local/bin/k3s-killall.sh
curl --insecure -v https://localhost 

sudo cp /etc/rancher/k3s/k3s.yaml /etc/rancher/k3s/k3s.yaml.orig
sudo rm /etc/rancher/k3s/k3s.yaml

# also make sure to remove `export KUBECONFIG=/etc/rancher/k3s/k3s.yaml` from .zshrc
sudo /usr/local/bin/k3s-killall.sh
curl --insecure -v https://localhost 


# start crc
crc start -p pull-secret.txt
```

## Useful Commands

```bash
# Stop the cluster
crc stop

# Delete the cluster
crc delete

# View cluster status
crc status

# Get console URL and credentials
crc console --credentials

# Clean up CRC installation
crc cleanup
```

Started the OpenShift cluster.

The server is accessible via web console at:
  https://console-openshift-console.apps-crc.testing

Log in as administrator:
  Username: kubeadmin
  Password: FztLV-V3ucr-stuTj-5pcLb

Log in as user:
  Username: developer
  Password: developer

## Port 443 debugging

```bash
curl --insecure -v https://localhost

sudo lsof -i :443

sudo lsof -i -P -n | grep LISTEN

sudo iptables -t nat -L -n -v
```


## Treafik Problem

```bash
kubectl get crds | grep traefik
kubectl apply -f https://raw.githubusercontent.com/traefik/traefik/v3.0/docs/content/reference/dynamic-configuration/kubernetes-crd-definition-v1.yml
kubectl rollout restart deployment -n kube-system traefik

# Get the new pod name
TRAEFIK_POD=$(kubectl get pods -n kube-system -l "app.kubernetes.io/name=traefik" -o jsonpath='{.items[0].metadata.name}')

# Check the new logs
kubectl logs $TRAEFIK_POD -n kube-system
```