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

  eip_id = huaweicloud_vpc_eip.mlrun-eip.id

  tags = {
    env  = "${var.env_prefix}"
  }
}