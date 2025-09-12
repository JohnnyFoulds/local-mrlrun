# Dedicated ELB (performance) for ingress
data "huaweicloud_availability_zones" "zones" {}

output "availability_zones" {
  value = data.huaweicloud_availability_zones.zones.names
}

output "subnet_az" {
  value = huaweicloud_vpc_subnet.subnet.availability_zone
  
}

resource "huaweicloud_elb_loadbalancer" "mlrun_elb_ingress" {
  name               = "${var.env_prefix}-elb-ingress"
  vpc_id             = huaweicloud_vpc.vpc.id
  ipv4_subnet_id     = huaweicloud_vpc_subnet.subnet.ipv4_subnet_id
  ipv4_eip_id        = huaweicloud_vpc_eip.mlrun_eip.id
  availability_zone  = [data.huaweicloud_availability_zones.zones.names[0]]

  depends_on = [ huaweicloud_vpc_subnet.subnet, huaweicloud_vpc_eip.mlrun_eip ]
}


resource "helm_release" "ingress_nginx" {
  name             = "ingress-nginx"
  namespace        = "ingress-nginx"
  create_namespace = true
  repository       = "https://kubernetes.github.io/ingress-nginx"
  chart            = "ingress-nginx"
  timeout          = 600
  
  set = [
    # Service type -> triggers ELB provisioning
    { 
        name = "controller.service.type"
        value = "LoadBalancer"
    },
    # REQUIRED on Autopilot: performance ELB class
    {
        name  = "controller.service.annotations.kubernetes\\.io/elb\\.class"
        value = "performance"
    },
    {
        name  = "controller.service.annotations.kubernetes\\.io/elb\\.id"
        value = huaweicloud_elb_loadbalancer.mlrun_elb_ingress.id
    },
    # {
    #     name  = "controller.service.annotations.kubernetes\\.io/elb\\.custom-eip-id"
    #     value = huaweicloud_vpc_eip.mlrun_eip.id
    # }
  ]

#   depends_on = [ huaweicloud_vpc_eip.mlrun_eip ]
}

# Discover the ELB address provisioned for the controller Service
data "kubernetes_service" "ingress_ctrl" {
  metadata {
    name      = "ingress-nginx-controller"
    namespace = "ingress-nginx"
  }
  depends_on = [helm_release.ingress_nginx]
}

locals {
  elb_ip        = try(data.kubernetes_service.ingress_ctrl.status[0].load_balancer[0].ingress[0].ip, "")
  elb_hostname  = try(data.kubernetes_service.ingress_ctrl.status[0].load_balancer[0].ingress[0].hostname, "")
  external_addr = coalesce(local.elb_ip, local.elb_hostname)
}

# display the elb values
output "elb_ip" {
  value = local.elb_ip
}

output "elb_hostname" {
  value = local.elb_hostname
}

output "external_addr" {
  value = local.external_addr
}
