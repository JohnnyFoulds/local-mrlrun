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

# CRITICAL STEP: Label the namespace to enable automatic CA injection
sudo kubectl label namespace mlrun trust.cert-manager.io/inject=true  
```

## Create Secrets

```bash
# Create the Kubernetes secret for authentication from the htpasswd file
sudo kubectl create secret generic registry-auth \
  --from-file=htpasswd=/home/johnny/auth/htpasswd \
  -n mlrun
```

## Request Certificate

```bash
# Create a file named registry-certificate.yaml
cat > registry-certificate.yaml <<EOF
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: registry-certificate
  namespace: mlrun
spec:
  # The name of the secret where the certificate will be stored
  secretName: registry-tls
  
  # Reference the ClusterIssuer we created in Step 2
  issuerRef:
    name: selfsigned-ca
    kind: ClusterIssuer

  # The domain names the certificate should be valid for.
  # These match the Kubernetes service names.
  dnsNames:
  - registry-service
  - registry-service.mlrun
  - registry-service.mlrun.svc
  - registry-service.mlrun.svc.cluster.local
EOF

# Request the certificate
sudo kubectl apply -f registry-certificate.yaml
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
curl https://registry-service.mlrun.svc.cluster.local:5000/v2/
```