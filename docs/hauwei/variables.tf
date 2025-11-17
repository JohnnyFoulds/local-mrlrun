variable "region"     { 
  type = string 
}

variable "access_key" {
  type = string
  sensitive = true
}

variable "secret_key" {
  type = string
  sensitive = true
}

variable "env_prefix" {
  type = string
  description = "The environment prefix for all resources"
  default     = "mlrun"
}

variable "kube_default_sc_name" {
  type        = string
  description = "Existing StorageClass to mark as default (e.g., csi-disk)"
  default     = "csi-disk"
}

variable "kubeconfig_path"  {
  type = string
  default = "kubeconfig_autopilot.yaml"
}

variable "kube_context" {
  type = string
  default = "external" # use "internal" if you don't expose EIP
} 