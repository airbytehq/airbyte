provider "aws" {
  region = "us-east-1"
  shared_credentials_file = "~/.aws/credentials"
}

module "airbyte-instance" {
  source = "./core"

  name = var.name

  default-sg = var.default-sg
  instance-size = var.instance-size
  key-name = var.key-name
  ami_id = var.ami-id
}

module "public-lb" {
  source = "./lb"

  name = var.name

  vpc = var.vpc
  subnets = var.subnets
  default-sg = var.default-sg
  certificate = var.certificate
  instance-id = module.airbyte-instance.instance-id
  auth-secret = var.auth-secret
}
