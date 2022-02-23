# Iteration: 1625064074

terraform {
  backend "s3" {
    bucket         = "vts-ctprd-074505835657-terraform-backend"
    dynamodb_table = "vts-ctprd-074505835657-terraform-backend"
    key            = "deployment/airbyte_stg/us_east_2/terraform.tfstate"
    region         = "us-east-1"
    role_arn       = "arn:aws:iam::074505835657:role/PlatformAdmin"
    session_name   = "stg_074505835657_deployment"
  }
}
