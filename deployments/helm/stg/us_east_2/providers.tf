# Iteration: 1625064074

provider "aws" {
  assume_role {
    role_arn     = "arn:aws:iam::074505835657:role/PlatformAdmin"
    session_name = "ctprd_074505835657_stg_deployment"
  }
  region = "us-east-2"
}

provider "kustomization" {}