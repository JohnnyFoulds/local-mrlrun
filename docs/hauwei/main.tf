# MLRun Bucket
resource "huaweicloud_obs_bucket" "mlrun-bucket" {
  bucket = "${var.env_prefix}-bucket"
  acl    = "private"
  tags = {
    type = "bucket"
    env  = "${var.env_prefix}"
  }
}

# Software Repository for Containers
resource "huaweicloud_swr_organization" "mlrun-swr-org" {
  name = "${var.env_prefix}-org"
}

