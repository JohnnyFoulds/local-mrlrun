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

# https://github.com/MatheusFarias03/TerraformChallenge/blob/7359a2bfe654ac7fecf1963fd495ff7bedc15f62/TF_FILES/main.tf#L65
# output "swr_org_region" {
#   value       = huaweicloud_swr_organization.mlrun-swr-org.region
#   description = "Region used for the SWR organization"
# }