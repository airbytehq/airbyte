terraform {
  backend "remote" {
    organization = "airbyte"

    workspaces {
      name = "aws-demo"
    }
  }

  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "3.24.1"
    }
  }
}
