# Local Docker Registry

## Create Certificates

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
sudo kubectl create secret generic registry-auth \
  --from-file=htpasswd=/home/johnny/auth/htpasswd \
  -n mlrun
```