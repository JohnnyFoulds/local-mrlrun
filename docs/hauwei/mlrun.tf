# create the mlrun namespace
resource "kubernetes_namespace" "mlrun" {
  metadata { name = "mlrun" }
  depends_on = [local_sensitive_file.kubeconfig]
}

# create the secret in the mlrun namespace
resource "kubernetes_secret" "registry_credentials" {
  metadata {
    name      = "registry-credentials"
    namespace = kubernetes_namespace.mlrun.metadata[0].name
  }

  type = "kubernetes.io/dockerconfigjson"
  
  data = {
    ".dockerconfigjson" = jsonencode({
      auths = {
        "${local.docker_server}" = { 
          username = local.docker_username
          password = local.docker_password
        }
      }
    })
  }
}

# resource "helm_release" "mlrun_ce" {
#   name             = "mlrun-ce"
#   namespace        = "mlrun"
#   create_namespace = false
#   repository       = "https://mlrun.github.io/ce"
#   chart            = "mlrun-ce"
# }
