locals {
  k8s_namespace_name_airbyte = "airbyte"
}

data "aws_eks_cluster" "cluster" {
  provider = aws.workload_us_east_2
  name     = "main"
}

data "aws_eks_cluster_auth" "cluster" {
  provider = aws.workload_us_east_2
  name     = "main"
}

provider "kubernetes" {
  alias                  = "airbyte"
  host                   = data.aws_eks_cluster.cluster.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority.0.data)
  token                  = data.aws_eks_cluster_auth.cluster.token
}

data "sops_file" "airbyte" {
  source_file = "enc.stg.yaml"
}

resource "kubernetes_namespace" "airbyte" {
  metadata {
    name = local.k8s_namespace_name_airbyte
  }
  provider = kubernetes.airbyte
}

resource "kubernetes_secret" "airbyte_secrets" {
  metadata {
    name      = "airbyte-secrets"
    namespace = "airbyte"
  }
  data       = data.sops_file.airbyte.data
  provider   = kubernetes.airbyte
}

data "kustomization" "airbyte_deployment" {
  path = "../../../kustomize"
}

resource "kustomization_resource" "airbyte_deployment" {
  for_each = data.kustomization.airbyte_deployment.ids

  manifest = data.kustomization.airbyte_deployment.manifests[each.value]
}