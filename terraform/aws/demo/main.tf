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
}

module "public-lb" {
  source = "./lb/public"

  name = var.name

  vpc = var.vpc
  subnets = var.subnets
  default-sg = var.default-sg
  certificate = var.certificate
  instance-id = module.airbyte-instance.instance-id
}

module "admin-lb" {
  source = "./lb/admin"

  name = var.name

  vpc = var.vpc
  subnets = var.subnets
  default-sg = var.default-sg
  instance-id = module.airbyte-instance.instance-id
}
