provider "huaweicloud" {
  region     = var.region
  access_key = var.access_key
  secret_key = var.secret_key    
}

provider "kubernetes" {
  config_path    = local_sensitive_file.kubeconfig.filename
  config_context = var.kube_context
}

provider "helm" {
  kubernetes = {
    config_path    = local_sensitive_file.kubeconfig.filename
    config_context = var.kube_context
  }
}