variable "name" {
  type = string
  default = "airbyte"
}

variable "domain" {
  type = string
  default = "demo.airbyte.io"
}

variable "instance_type" {
  type = string
  default = "e2-standard-4"
}

variable "project" {
  type = string
  default = "airbyte-production"
}

variable "region" {
  type = string
  default = "us-central1"
}

variable "zone" {
  type = string
  default = "us-central1-a"
}

variable "network" {
  type = string
  default = "default"
}

provider "google" {
  project = var.project
  region = var.region
  zone = var.zone
}

resource "google_compute_instance" "core" {
  name = "${var.name}-core"
  machine_type = var.instance_type

  metadata_startup_script = file("${path.module}/init.sh")

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-10"
    }
  }

  network_interface {
    network = var.network
    access_config {}
  }
}

resource "google_compute_firewall" "health_checks" {
  name = "allow-health-checks"
  network = var.network

  source_ranges = [
    "130.211.0.0/22",
    "35.191.0.0/16"
  ]

  allow {
    protocol = "tcp"
    ports = ["0-65535"]
  }
}

resource "google_compute_instance_group" "core" {
  name = "${var.name}-core"
  description = "Airbyte core instance group"

  instances = [
    google_compute_instance.core.id,
  ]

  named_port {
    name = "http-webapp"
    port = 8000
  }

  named_port {
    name = "http-api"
    port = 8001
  }
}

resource "google_compute_health_check" "webapp" {
  name = "${var.name}-webapp"

  timeout_sec = 1
  check_interval_sec = 1

  http_health_check {
    port = 8000
    request_path = "/"
  }
}

resource "google_compute_backend_service" "webapp" {
  name = "${var.name}-webapp"
  health_checks = [google_compute_health_check.webapp.id]

  port_name = "http-webapp"

  backend {
    group = google_compute_instance_group.core.id
  }
}

resource "google_compute_health_check" "api" {
  name = "${var.name}-api"

  timeout_sec = 1
  check_interval_sec = 1

  http_health_check {
    port = 8001
    request_path = "/api/v1/health"
  }
}

resource "google_compute_backend_service" "api" {
  name = "${var.name}-api"
  health_checks = [google_compute_health_check.api.id]

  port_name = "http-api"

  backend {
    group = google_compute_instance_group.core.id
  }
}

resource "google_compute_url_map" "core" {
  name = var.name

  default_service = google_compute_backend_service.webapp.id

  host_rule {
    hosts = ["*"]
    path_matcher = "allpaths"
  }

  path_matcher {
    name = "allpaths"

    default_service = google_compute_backend_service.webapp.id

    path_rule {
      paths = ["/api/v1/*"]
      service = google_compute_backend_service.api.id
    }
  }
}

resource "google_compute_managed_ssl_certificate" "airbyte" {
  name = "${var.name}-certificate"

  managed {
    domains = [var.domain]
  }
}

resource "google_compute_target_https_proxy" "airbyte" {
  name = "${var.name}-https-proxy"

  url_map = google_compute_url_map.core.id
  ssl_certificates = [google_compute_managed_ssl_certificate.airbyte.id]
}

resource "google_compute_global_forwarding_rule" "airbyte" {
  name = "${var.name}-forwarding-rule"

  port_range = 443
  target = google_compute_target_https_proxy.airbyte.id
}
