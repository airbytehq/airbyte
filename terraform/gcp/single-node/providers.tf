provider "google" {
  project     = "dataline-integration-testing"
  region      = "us-central1"
  zone        = "us-central1-c"
}

terraform {
  required_providers {
    google = {
      version = "~> 3.66.1"
    }
  }
}
