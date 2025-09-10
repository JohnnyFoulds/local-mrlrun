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

# variable "kubeconfig_path"  {
#   type = string
#   default = "kubeconfig_autopilot.yaml"
# }