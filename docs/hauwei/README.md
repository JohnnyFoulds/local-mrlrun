# Huawei Public Cloud Deployment Guide

This document provides a comprehensive guide to deploying the MLRun framework on the Huawei public cloud platform. It covers the necessary steps, configurations, and best practices to ensure a successful deployment.

## Authentication

You can use Terraform to orchestrate diverse cloud resources on HUAWEI CLOUD. Before using Terraform, obtain AK/SK and configure Terraform to complete authentication.

Configure the region, AK, and SK as environment variables. For example:

```bash
export HW_REGION_NAME="cn-north-1"
export HW_ACCESS_KEY="my-access-key"
export HW_SECRET_KEY="my-secret-key"
```

## Install Terraform

```bash
wget -O - https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(grep -oP '(?<=UBUNTU_CODENAME=).*' /etc/os-release || lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform
```

### terraform init

```bash
# set -a && source ../../.env && set +a
terraform init
```

## References

- [Install Terraform](https://developer.hashicorp.com/terraform/install)
- [Huawei Cloud Terraform Quick Start](https://support.huaweicloud.com/intl/en-us/qs-terraform/index.html)
- [Getting Started With Terraform on Huawei Cloud](https://www.youtube.com/watch?v=0uH9G3i_krM)
- [Terraform Provider](https://registry.terraform.io/providers/huaweicloud/huaweicloud/latest/docs)
- [Learn it from Zero: Terraform Basics on Huawei Public Cloud](https://medium.com/huawei-developers/%EF%B8%8F-learn-it-from-zero-terraform-basics-on-huawei-public-cloud-e28802dfe65a)
- [Configuring the Network](https://support.huaweicloud.com/intl/en-us/usermanual-terraform/terraform_0008.html)
- [Push Image](https://github.com/MatheusFarias03/TerraformChallenge/blob/7359a2bfe654ac7fecf1963fd495ff7bedc15f62/TF_FILES/main.tf#L65)
