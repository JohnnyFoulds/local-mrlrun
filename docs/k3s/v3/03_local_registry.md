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

sudo kubectl get secret ca-key-pair -n cert-manager -o jsonpath='{.data.ca\.crt}' | base64 -d > ca.crt

sudo kubectl create configmap ca-certificates \
  --from-file=ca-certificates.crt=ca.crt \
  -n mlrun
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
  name: registry-service-cert
  namespace: mlrun
spec:
  secretName: registry-tls
  issuerRef:
    name: selfsigned-ca
    kind: ClusterIssuer
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
#sudo kubectl exec -it nginx -- curl --insecure -v https://registry-service.mlrun.svc.cluster.local:5000/v2/
```

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