# # NGINX Ingress Controller (public ELB)
# resource "helm_release" "ingress_nginx" {
#   name             = "ingress-nginx"
#   namespace        = "ingress-nginx"
#   create_namespace = true
#   repository       = "https://kubernetes.github.io/ingress-nginx"
#   chart            = "ingress-nginx"
#   timeout          = 600

#   set = [
#     { 
#         name = "controller.service.type"
#         value = "LoadBalancer"
#     }
#   ]
# }

# # Discover the ELB address provisioned for the controller Service
# data "kubernetes_service" "ingress_ctrl" {
#   metadata {
#     name      = "ingress-nginx-controller"
#     namespace = "ingress-nginx"
#   }
#   depends_on = [helm_release.ingress_nginx]
# }

# locals {
#   elb_ip        = try(data.kubernetes_service.ingress_ctrl.status[0].load_balancer[0].ingress[0].ip, "")
#   elb_hostname  = try(data.kubernetes_service.ingress_ctrl.status[0].load_balancer[0].ingress[0].hostname, "")
#   external_addr = coalesce(local.elb_ip, local.elb_hostname)
# }

# # display the elb values
# output "elb_ip" {
#   value = local.elb_ip
# }

# output "elb_hostname" {
#   value = local.elb_hostname
# }

# output "external_addr" {
#   value = local.external_addr
# }
