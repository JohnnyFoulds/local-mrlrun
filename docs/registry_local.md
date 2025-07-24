# Local Docker Registry'

## References

- [How to Set Up a Local Docker Registry](https://www.youtube.com/watch?v=fAIM1oaEzMI)
- [How to Use Your Own Registry](https://www.docker.com/blog/how-to-use-your-own-registry-2/)
- [Distribution:registry](https://hub.docker.com/_/registry)
- [Distribution Registry](https://distribution.github.io/distribution/about/deploying/)
- https://github.com/yonishelach/nvidia-data-flywheel/blob/78d08369ecbb6a6772444cae65d5a7c51160e227/scripts/mlrun.sh#L43

## Create a Local Docker Registry

```bash
# create password
mkdir auth

docker run \
  --entrypoint htpasswd \
  httpd:2 -Bbn mlrun mlpass > auth/htpasswd

# run the container
docker run -d -p 6500:5000 --restart=always --name registry \
  -v /home/johnny/swan/opt/registry:/var/lib/registry \
  -v /home/johnny/auth:/auth \
  -e "REGISTRY_AUTH=htpasswd" \
  -e "REGISTRY_AUTH_HTPASSWD_REALM=Registry Realm" \
  -e REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd \
  registry:3

# insecure registry configuration
docker info| grep -A 20 "Insecure Registries"
sudo vi /etc/docker/daemon.json

# add the following lines
"insecure-registries" : ["dragon:6500"]

# restart docker
sudo systemctl restart docker

# log into the registry
docker login dragon:6500
docker login localhost:6500
```

## Create Secret for MLRun

```bash
# delete the old secret
sudo kubectl delete secret registry-credentials -n mlrun

# create a new secret
sudo kubectl --namespace mlrun create secret docker-registry registry-credentials \
    --from-file=/home/johnny/.docker/config.json

# validate the secret
sudo kubectl get secrets -n mlrun
```

## Update MLRun `global.registry.url`

```bash
# Create a configmap for local docker registry:
# sudo kubectl create configmap registry-config \
#   --namespace=mlrun \
#   --kubeconfig /etc/rancher/k3s/k3s.yaml \
#   --from-literal=insecure_pull_registry_mode=enabled \
#   --from-literal=insecure_push_registry_mode=enabled
    
sudo helm -n mlrun upgrade mlrun-ce mlrun-ce/mlrun-ce \
  --kubeconfig /etc/rancher/k3s/k3s.yaml \
  --reuse-values \
  --set global.registry.url=dragon:6500 \
  --set global.registry.secretName=registry-credentials \
  --set mlrun.httpdb.builder.dockerRegistry="dragon:6500" \
  --set mlrun.httpdb.builder.insecurePullRegistryMode=enabled \
  --set mlrun.httpdb.builder.insecurePushRegistryMode=enabled


  #--set builder.docker_registry=dragon:6500 \
  #--set builder.docker_registry_secret=registry-credentials \

#   --set builder.insecure_push_registry_mode=enabled \
#   --set builder.insecure_pull_registry_mode=enabled \
#   --set mlrun.builder.insecurePullRegistry=true \
#   --set mlrun.builder.insecurePushRegistry=true

## junk
# sudo kubectl --kubeconfig /etc/rancher/k3s/k3s.yaml -n mlrun set env deployment/mlrun-api-chief \
#   MLRUN_HTTPDB__BUILDER__INSECURE_PULL_REGISTRY=true \
#   MLRUN_HTTPDB__BUILDER__INSECURE_PUSH_REGISTRY=true

# sudo kubectl --kubeconfig /etc/rancher/k3s/k3s.yaml -n mlrun rollout status deployment/mlrun-api-chief

# sudo kubectl --kubeconfig /etc/rancher/k3s/k3s.yaml -n mlrun exec deploy/mlrun-api-chief -- env | grep INSECURE

# sudo kubectl --kubeconfig /etc/rancher/k3s/k3s.yaml -n mlrun set env deployment/mlrun-api-worker \
#   MLRUN_HTTPDB__BUILDER__INSECURE_PULL_REGISTRY=true \
#   MLRUN_HTTPDB__BUILDER__INSECURE_PUSH_REGISTRY=true

# sudo kubectl --kubeconfig /etc/rancher/k3s/k3s.yaml -n mlrun rollout status deployment/mlrun-api-worker

# WORKER_POD=$(sudo kubectl --kubeconfig /etc/rancher/k3s/k3s.yaml -n mlrun get pods -l mlrun/component=api-worker -o jsonpath='{.items[0].metadata.name}')
# sudo kubectl --kubeconfig /etc/rancher/k3s/k3s.yaml -n mlrun exec $WORKER_POD -- env | grep INSECURE

# sudo helm --namespace mlrun \
#     --kubeconfig /etc/rancher/k3s/k3s.yaml \
#     upgrade mlrun-ce mlrun-ce/mlrun-ce \
#     --reuse-values \
#     --set mlrun.builder.extraKanikoArgs="--insecure"

# sudo helm --namespace mlrun \
#     --kubeconfig /etc/rancher/k3s/k3s.yaml \
#     upgrade mlrun-ce mlrun-ce/mlrun-ce \
#     --reuse-values \
#     --set mlrun.httpdb.builder.insecurePullRegistryMode=enabled \
#     --set mlrun.httpdb.builder.insecurePushRegistryMode=enabled

# Set the correct variable on the chief
sudo kubectl --kubeconfig /etc/rancher/k3s/k3s.yaml -n mlrun set env deployment/mlrun-api-chief \
  MLRUN_HTTPDB__BUILDER__INSECURE_PULL_REGISTRY_MODE=enabled \
  MLRUN_HTTPDB__BUILDER__INSECURE_PUSH_REGISTRY_MODE=enabled

# Set the correct variable on the worker
sudo kubectl --kubeconfig /etc/rancher/k3s/k3s.yaml -n mlrun set env deployment/mlrun-api-worker \
  MLRUN_HTTPDB__BUILDER__INSECURE_PULL_REGISTRY_MODE=enabled \
  MLRUN_HTTPDB__BUILDER__INSECURE_PUSH_REGISTRY_MODE=enabled

sudo tee /etc/rancher/k3s/registries.yaml > /dev/null <<EOF
mirrors:
  "dragon:6500":
    endpoint:
      - "http://dragon:6500"
EOF

# restart
sudo systemctl stop k3s
sudo systemctl start k3s
```

## Load Images

```bash
docker pull mlrun/mlrun-gpu:1.7.2
docker tag mlrun/mlrun-gpu:1.7.2 dragon:6500/mlrun/mlrun-gpu:1.7.2
docker push dragon:6500/mlrun/mlrun-gpu:1.7.2
docker rmi mlrun/mlrun-gpu:1.7.2
docker rmi dragon:6500/mlrun/mlrun-gpu:1.7.2

# verify push
curl http://dragon:6500/v2/_catalog
curl http://dragon:6500/v2/mlrun/mlrun-gpu/tags/list
```

## Watch the Logs

```bash
docker logs -f registry
```

kubectl -n mlrun get pods | grep builder