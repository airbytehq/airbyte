terraform {
  backend "s3" {
    bucket         = "vts-ctprd-375060456233-terraform-backend"
    dynamodb_table = "vts-ctprd-375060456233-terraform-backend"
    key            = "deployment/airbyte_stg/us_east_2/terraform.tfstate"
    region         = "us-east-1"
    role_arn       = "arn:aws:iam::375060456233:role/PlatformAdmin"
    session_name   = "dev_375060456233_deployment"
  }
}
