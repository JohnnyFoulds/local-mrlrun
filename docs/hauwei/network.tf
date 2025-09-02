# Create a VPC
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
}

# Security Group
resource "huaweicloud_networking_secgroup" "secgroup" {
  name                 = "${var.env_prefix}-secgroup"
  description          = "MLRun security group"
  delete_default_rules = true
}

# Security Group Rules
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