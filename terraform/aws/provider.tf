terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.50.0"
    }
  }
  backend "s3" {
    bucket = "com-airbyte-terraform-state"
    region = "us-east-2"
    key    = "projects/main/terraform.state"
    dynamodb_table = "terraform-state-lock-dynamo"
  }
}

provider "aws" {
  region = "us-east-2"
}

