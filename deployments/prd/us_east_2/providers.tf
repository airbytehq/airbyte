# Iteration: 1625064074

provider "aws" {
  alias = "workload_us_east_2"
  assume_role {
    role_arn     = "arn:aws:iam::375060456233:role/PlatformAdmin"
    session_name = "ctprd_375060456233_prd_deployment"
  }
  region = "us-east-2"
}

provider "kustomization" {
  kubeconfig_path = "~/.kube/config"
}