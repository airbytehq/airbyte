terraform {
  required_providers {
    snowflake = {
      source  = "Snowflake-Labs/snowflake"
      version = "~> 0.55.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 4.65.0"
    }
  }

  backend "gcs" {
    bucket = "hackdays-2023-05-terraform-integration-test-envs"
  }
}

provider "google" {
  project = "dataline-integration-testing"
}

provider "snowflake" {
  # Source the .env file to add the required environment variables
  # Make sure you've signed into lpass cli
  # lpass login joseph.bell@airbyte.io
  # source ./.env
  role = "securityadmin"
  alias = "securityadmin"
}

provider "snowflake" {
  # Source the .env file to add the required environment variables
  # Make sure you've signed into lpass cli
  # lpass login joseph.bell@airbyte.io
  # source ./.env
  role = "sysadmin"
  alias = "sysadmin"
}
