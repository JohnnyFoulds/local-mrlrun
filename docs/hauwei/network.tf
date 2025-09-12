# -------------------------------
# VPC + Subnet
# -------------------------------
resource "huaweicloud_vpc" "vpc" {
  name = "${var.env_prefix}-vpc"
  cidr = "192.168.0.0/16"
}

# Subnet
resource "huaweicloud_vpc_subnet" "subnet" {
  name       = "${var.env_prefix}-subnet"
  cidr       = "192.168.0.0/24"
  gateway_ip = "192.168.0.1"
  vpc_id     = huaweicloud_vpc.vpc.id

  # DNS values are required for CCE node installation per Huawei docs
  primary_dns   = "100.125.1.250"
  secondary_dns = "100.125.21.250"
}

# -------------------------------
# EIP for API server
# -------------------------------
resource "huaweicloud_vpc_eip" "mlrun_eip" {
  publicip {
    type = "5_bgp"
  }
  bandwidth {
    name        = "${var.env_prefix}-eip-bandwidth"
    size        = 8
    share_type  = "PER"
    charge_mode = "traffic"
  }
}
# -------------------------------
# Security Group
# -------------------------------
resource "huaweicloud_networking_secgroup" "secgroup" {
  name                 = "${var.env_prefix}-secgroup"
  description          = "MLRun security group"
  delete_default_rules = true
}

# Ingress rules
resource "huaweicloud_networking_secgroup_rule" "secgroup_rule_http" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 80
  port_range_max    = 80
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = huaweicloud_networking_secgroup.secgroup.id
}

resource "huaweicloud_networking_secgroup_rule" "secgroup_rule_ssh" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = huaweicloud_networking_secgroup.secgroup.id
}

# Egress rules
# resource "huaweicloud_networking_secgroup_rule" "secgroup_rule_egress_all" {
#   direction         = "egress"
#   ethertype         = "IPv4"
#   # no protocol/ports -> allow all egress
#   remote_ip_prefix  = "0.0.0.0/0"
#   security_group_id = huaweicloud_networking_secgroup.secgroup.id
# }

# -------------------------------
# NAT Gateway
# -------------------------------
# Dedicated EIP for NAT (keep mlrun-eip for API server)
resource "huaweicloud_vpc_eip" "mlrun_nat_eip" {
  publicip { type = "5_bgp" }
  bandwidth {
    name        = "${var.env_prefix}-nat-bw"
    size        = 10
    share_type  = "PER"
    charge_mode = "traffic"
  }
}

# NAT Gateway in same VPC/subnet as the cluster
resource "huaweicloud_nat_gateway" "mlrun_nat" {
  name      = "${var.env_prefix}-nat"
  spec      = "1"                                   # small
  vpc_id    = huaweicloud_vpc.vpc.id
  subnet_id = huaweicloud_vpc_subnet.subnet.id
}

# SNAT rule: allow all IPs in the cluster subnet to reach Internet via NAT EIP
resource "huaweicloud_nat_snat_rule" "snat_all" {
  nat_gateway_id = huaweicloud_nat_gateway.mlrun_nat.id
  subnet_id      = huaweicloud_vpc_subnet.subnet.id
  floating_ip_id = huaweicloud_vpc_eip.mlrun_nat_eip.id
}