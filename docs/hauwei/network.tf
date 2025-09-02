# Create a VPC
resource "huaweicloud_vpc" "mlrun_vpc" {
  name = "mlrun_vpc"
  cidr = "192.168.0.0/16"
}