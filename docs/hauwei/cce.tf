resource "huaweicloud_cce_autopilot_cluster" "mlrun-cluster" {
  name        = "${var.env_prefix}-cluster"
  flavor      = "cce.autopilot.cluster"
  description = "MLRun CCE Autopilot Cluster"

  host_network {
    vpc    = huaweicloud_vpc.vpc.id
    subnet = huaweicloud_vpc_subnet.subnet.id
  }

  container_network {
    mode = "eni"
  }

  eni_network {
    subnets {
      subnet_id = huaweicloud_vpc_subnet.subnet.ipv4_subnet_id
    }
  }

  eip_id = huaweicloud_vpc_eip.mlrun_eip.id

  tags = {
    env  = "${var.env_prefix}"
  }
}

# resource "kubernetes_manifest" "mlrun_mark_default_sc" {
#   manifest = {
#     apiVersion = "storage.k8s.io/v1"
#     kind       = "StorageClass"
#     metadata = {
#       name        = var.kube_default_sc_name
#       annotations = {
#         "storageclass.kubernetes.io/is-default-class" = "true"
#       }
#     }
#     provisioner = "everest-csi-provisioner"  # Required for Huawei Cloud
#     parameters = {
#       "csi.storage.k8s.io/fstype" = "ext4"
#       "everest.io/disk-volume-type" = "SAS"  # or "SSD", "SATA"
#     }
#     volumeBindingMode = "WaitForFirstConsumer"
#     allowVolumeExpansion = true
#   }

#   depends_on = [
#     huaweicloud_cce_autopilot_cluster.mlrun-cluster
#   ]
# }