data "huaweicloud_cce_autopilot_cluster_certificate" "mlrun_cluster_cert" {
  cluster_id = huaweicloud_cce_autopilot_cluster.mlrun-cluster.id
  duration = 30
  depends_on = [huaweicloud_cce_autopilot_cluster.mlrun-cluster]
}

# Write kubeconfig to disk securely (avoid leaking to plan logs)
resource "local_sensitive_file" "kubeconfig" {
  filename        = var.kubeconfig_path
  content         = data.huaweicloud_cce_autopilot_cluster_certificate.mlrun_cluster_cert.kube_config_raw
  file_permission = "0600"
}