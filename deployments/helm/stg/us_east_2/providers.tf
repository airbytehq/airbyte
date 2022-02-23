# Iteration: 1625064074

provider "aws" {
  alias = "workload_us_east_2"
  assume_role {
    role_arn     = "arn:aws:iam::074505835657:role/PlatformAdmin"
    session_name = "ctprd_074505835657_stg_deployment"
  }
  region = "us-east-2"
}

data "terraform_remote_state" "customization" {
  backend = "s3"
  config = {
    bucket         = "vts-prd-terraform-backend"
    dynamodb_table = "vts-prd-terraform-backend"
    key            = "vts-prd-ct-074505835657/customizations/us-east-1/terraform.tfstate"
    region         = "us-east-1"
    role_arn       = "arn:aws:iam::856154240248:role/PlatformAdmin"
    session_name   = "prd_vts_ctprd_data_stg_customizations"
  }
}

provider "kustomization" {
  kubeconfig_raw = data.terraform_remote_state.customization.outputs.kubeconfig
}