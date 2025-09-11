terraform {
  required_providers {
    huaweicloud = {
      source = "huaweicloud/huaweicloud"
      version = ">= 1.78.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.29.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = ">= 3.0.2"
    }
    local = {
      source  = "hashicorp/local"
      version = ">= 2.5.1"
    }
  }
}
