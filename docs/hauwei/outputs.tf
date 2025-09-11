output "region" {
  value = var.region
}

output "swr_org" {
  value = huaweicloud_swr_organization.mlrun-swr-org.name
  depends_on = [ huaweicloud_swr_organization.mlrun-swr-org ]
}

# https://github.com/MatheusFarias03/TerraformChallenge/blob/7359a2bfe654ac7fecf1963fd495ff7bedc15f62/TF_FILES/main.tf#L65
output "swr_org_region" {
  value       = huaweicloud_swr_organization.mlrun-swr-org.region
  description = "Region used for the SWR organization"
}

output "swr_login_server" {
  value = huaweicloud_swr_organization.mlrun-swr-org.login_server
}

output "cluster_id" {
  value = huaweicloud_cce_autopilot_cluster.mlrun-cluster.id
}

output "cluster_name"   {
    value = huaweicloud_cce_autopilot_cluster.mlrun-cluster.name
}

output "kubeconfig_path" {
  value = local_sensitive_file.kubeconfig.filename
}

output "docker_server" {
    value = local.docker_server
}

output "docker_username" {
    value = local.docker_username
    sensitive = true
}

# debug: terraform output -raw docker_password
output "docker_password" {
    value = local.docker_password
    sensitive = true
}