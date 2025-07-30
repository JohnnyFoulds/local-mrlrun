# Local Docker Registry

## Create Certificates

```bash
# Create a directory for the certs
mkdir -p /home/johnny/certs/CA

# Create a private key
openssl genrsa -out /home/johnny/certs/domain.key 4096

# Create a certificate signing request
openssl req -new -key /home/johnny/certs/domain.key \
  -out /home/johnny/certs/domain.csr \
  -subj "/C=US/ST=CA/L=PaloAlto/O=IT/CN=registry.mlrun.svc.cluster.local"

# Create SAN config file
cat > /home/johnny/certs/domain.ext <<EOF
subjectAltName = @alt_names

[alt_names]
DNS.1 = dragon
DNS.2 = registry
DNS.3 = registry.mlrun
DNS.4 = registry.mlrun.svc
DNS.5 = registry.mlrun.svc.cluster.local
EOF

# Self-sign the certificate with the SAN extension
openssl x509 -req -in /home/johnny/certs/domain.csr \
  -signkey /home/johnny/certs/domain.key \
  -out /home/johnny/certs/domain.crt \
  -days 365 -sha256 -extfile /home/johnny/certs/domain.ext
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

```bash
# Create a namespace for MLRun
sudo kubectl create namespace mlrun
```

## Crete Secrets

```bash
# TLS cert and key
sudo kubectl create secret tls registry-tls \
  --cert=/home/johnny/certs/domain.crt \
  --key=/home/johnny/certs/domain.key \
  -n mlrun

# htpasswd file
sudo kubectl create secret tls registry-tls \
  --cert=/home/johnny/certs/domain.crt \
  --key=/home/johnny/certs/domain.key \
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
curl -k https://dragon:30500/v2/
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
curl https://registry.mlrun.svc.cluster.local:5000/v2/
```