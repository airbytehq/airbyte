#
# Define all the variables that you might want to override
#

variable "name" {
  type = string
  default = "demo"
}

variable "vpc" {
  type = string
  default = "vpc-0e436274"
}

variable "default-sg" {
  type = string
  default = "sg-551dc903"
}

variable "subnets" {
  default = [
    "subnet-8a7d68ed",
    "subnet-2f45e062",
    "subnet-2eca9310",
    "subnet-cf8393e1",
    "subnet-64f0e638",
    "subnet-e9f33ce7"
  ]
}

variable "instance-size" {
  type = string
  default = "t3.medium"
}

variable "key-name" {
  type = string
  default = "airbyte-app"
}

variable "certificate" {
  type = string
  default = "arn:aws:acm:us-east-1:168714685353:certificate/c762da95-be91-466d-a9f0-1c22f449ae0d"
}

terraform {
  backend "remote" {
    organization = "airbyte"

    workspaces {
      name = "demo-aws"
    }
  }

  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "3.24.1"
    }
  }
}

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
  certificate = var.certificate
  instance-id = module.airbyte-instance.instance-id
}
