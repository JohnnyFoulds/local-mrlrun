# derive SWR login password (aka "login key") with OpenSSL
data "external" "swr_login_key" {
  program = ["bash", "-lc", <<-BASH
    set -euo pipefail
    AK='${var.access_key}'
    SK='${var.secret_key}'
    LOGIN_KEY=$(printf "%s" "$AK" | openssl dgst -binary -sha256 -hmac "$SK" | od -An -vtx1 | tr -d ' \n')
    printf '{"login_key":"%s"}' "$LOGIN_KEY"
  BASH
  ]
}

# set the docker details as locals
locals {
    docker_server = huaweicloud_swr_organization.mlrun-swr-org.login_server
    docker_org    = huaweicloud_swr_organization.mlrun-swr-org.name
    docker_username = "${huaweicloud_swr_organization.mlrun-swr-org.region}@${var.access_key}"
    docker_password = data.external.swr_login_key.result.login_key
}

