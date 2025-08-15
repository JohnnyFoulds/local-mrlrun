# NVIDIA GPU Operator

> ❗❗️❗️️The references are correct, but I am unable to get GPU Support with Open Shift Local due to virtualization.


## References

- [Node Feature Discovery Operator](https://docs.redhat.com/en/documentation/openshift_container_platform/4.18/html/specialized_hardware_and_driver_enablement/psap-node-feature-discovery-operator#install-operator-cli_psap-node-feature-discovery-operator)
- [NVIDIA GPU Operator with OpenShift Virtualization](https://docs.nvidia.com/datacenter/cloud-native/openshift/latest/openshift-virtualization.html)
- [Installing the Node Feature Discovery Operator on OpenShift](https://docs.nvidia.com/datacenter/cloud-native/openshift/latest/install-nfd.html)

## Installing the NFD Operator using the CLI

### 1. Create a namespace for the NFD Operator

```bash
cat <<EOF | oc create -f -
apiVersion: v1
kind: Namespace
metadata:
  name: openshift-nfd
  labels:
    name: openshift-nfd
    openshift.io/cluster-monitoring: "true"
EOF
```

### 2. Install the NFD Operator in the namespace

#### i. Create the `OperatorGroup`

```bash
cat <<EOF | oc create -f -
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  generateName: openshift-nfd-
  name: openshift-nfd
  namespace: openshift-nfd
spec:
  targetNamespaces:
  - openshift-nfd
EOF
```

#### ii. Create the following `Subscription`

```bash
cat <<EOF | oc create -f -
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: nfd
  namespace: openshift-nfd
spec:
  channel: "stable"
  installPlanApproval: Automatic
  name: nfd
  source: redhat-operators
  sourceNamespace: openshift-marketplace
EOF
```

#### iii. Create the NodeFeatureDiscovery Instance

```bash
cat <<EOF | oc apply -f -
apiVersion: nfd.openshift.io/v1
kind: NodeFeatureDiscovery
metadata:
  name: nfd-instance
  namespace: openshift-nfd
spec:
  operand:
    namespace: openshift-nfd
EOF
```

#### iv. Change to the openshift-nfd project.

```bash
oc project openshift-nfd

# verify that the Operator deployment is successful
oc get pods
```

## Install the NVIDIA GPU Operator

After a few minutes, you can verify that your GPU nodes are correctly labeled. Replace <your-gpu-node-name> with the name of a node that has a GPU.

```bash
oc get node crc --show-labels | grep 'feature.node.kubernetes.io/pci'
oc describe node | egrep 'Roles|pci' | grep -v master
```

It must find: `feature.node.kubernetes.io/pci-10de.present=true` 

> The next step would be to follow the [Installing the NVIDIA GPU Operator on OpenShift](https://docs.nvidia.com/datacenter/cloud-native/openshift/latest/install-gpu-ocp.html) guide.