# Install MLRun

## Docker Logins

```bash
docker login -u shambi
docker login -u mlrun dragon:30500

# repeat the password for the svc url
export AUTH=$(jq -r '.auths["dragon:30500"].auth' ~/.docker/config.json) && \
jq --arg auth "$AUTH" '.auths["http://registry-service.mlrun.svc.cluster.local:5000"] = {"auth": $auth}' ~/.docker/config.json > ~/.docker/config.new.json && \
mv ~/.docker/config.new.json ~/.docker/config.json
```

## Update Helm

```bash
helm repo add mlrun-ce https://mlrun.github.io/ce
helm repo list
helm repo update
```

## Create Registry Secret

```bash
kubectl --namespace mlrun create secret docker-registry registry-credentials \
    --from-file=/home/johnny/.docker/config.json

# validate the secret
kubectl get secrets -n mlrun
```

## Install MLRun

To install the chart with the release name `mlrun-ce` use the following command.
> `global.externalHostAddress` is the IP address of the host machine.

```bash
helm --namespace mlrun \
    install mlrun-ce \
    --set global.registry.url=registry-service.mlrun.svc.cluster.local:5000 \
    --set global.registry.secretName=registry-credentials \
    --set global.externalHostAddress=192.168.1.184 \
    --set nuclio.dashboard.externalIPAddresses=192.168.1.184 \
    mlrun-ce/mlrun-ce
```

In a separate terminal progress can be viewed with the following command:

```bash
sudo kubectl get pods -n mlrun -w
``` 