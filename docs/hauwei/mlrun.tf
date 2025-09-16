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

resource "helm_release" "mlrun_ce" {
  name              = "mlrun-ce"
  namespace         = "mlrun"
  create_namespace  = false
  repository        = "https://mlrun.github.io/ce"
  chart             = "mlrun-ce"
  wait              = true
  timeout           = 1200
  dependency_update = true
 
  set = [
     # docker registry settings
    {
      name = "global.registry.url"
      value = "${local.docker_server}/${local.docker_org}" 
    },
    { 
      name = "global.registry.secretName"
      value = kubernetes_secret.registry_credentials.metadata[0].name
    },

    # external access settings
    { 
      name = "global.externalHostAddress"
      value = local.elb_ip
    },
    {
      name = "nuclio.dashboard.externalIPAddresses",
      value = local.elb_ip
    },
    
    # select components not to install
    { name  = "jupyterNotebook.enabled", value = "false" },
    { name  = "sparkOperator.enabled", value = "false" },
    { name  = "kube-prometheus-stack.enabled", value = "false" },

    # use ClusterIP instead of NodePort for the internal services
    { name = "mlrun.api.service.type", value = "ClusterIP" },
    { name = "mlrun.ui.service.type", value = "ClusterIP" },
    { name = "minio.service.type", value = "ClusterIP" },
    { name = "minio.consoleService.type", value = "ClusterIP" },
    { name = "nuclio.dashboard.service.type", value = "ClusterIP" },
    { name = "global.nuclio.dashboard.nodePort", value = "" },
    { name = "pipelines.service.type", value = "ClusterIP" }
  ]

  depends_on = [
    helm_release.ingress_nginx,
    kubernetes_secret.registry_credentials,
    huaweicloud_vpcep_endpoint.swr_endpoint
  ] 
}
