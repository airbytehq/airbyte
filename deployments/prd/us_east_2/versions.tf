terraform {
  required_version = "~> 0.15.1"
  required_providers {
    aws = {
      version = "~> 3.46.0"
    }

    kustomization = {
      source  = "kbst/kustomization"
      version = "0.7.2"
    }

    sops = {
      source  = "carlpett/sops"
      version = "~> 0.6.2"
    }
  }
}
