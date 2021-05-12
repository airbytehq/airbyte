resource "google_compute_network" "airbyte-network" {
  name                    = "airbyte-network"
  auto_create_subnetworks = "false"
}

resource "google_compute_subnetwork" "airbyte-subnetwork" {
  name                     = "airbyte-subnetwork"
  ip_cidr_range            = "10.128.0.0/9"
  network                  = google_compute_network.airbyte-network.self_link
  private_ip_google_access = true
}

resource "google_compute_firewall" "allow-ssh" {
  name    = "test-firewall"
  network = google_compute_network.airbyte-network.self_link

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }
}

resource "google_compute_firewall" "allow-lb" {
  name    = "allow-lb-firewall"
  network = google_compute_network.airbyte-network.self_link

  allow {
    protocol = "tcp"
    ports    = ["8000", "8001"]
  }

  // allow load balancer ips to access
  source_ranges = ["35.191.0.0/16", "130.211.0.0/22"]
}

resource "google_compute_router" "airbyte-router" {
  name    = "airbyte-nat"
  network = google_compute_network.airbyte-network.self_link
}

resource "google_compute_router_nat" "airbyte-nat" {
  name                               = "airbyte-nat"
  router                             = google_compute_router.airbyte-router.name
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
}

resource "google_service_account" "airbyte-svc" {
  account_id   = "airbyte-svc"
  display_name = "airbyte-svc"
}

resource "google_project_iam_member" "airbyte-stackdriver-member" {
  role = "roles/monitoring.metricWriter"
  member = "serviceAccount:${google_service_account.airbyte-svc.email}"
}

resource "google_compute_instance" "airbyte-instance" {
  count        = 1
  name         = "airbyte-prod"
  machine_type = "n1-standard-4"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-9"
      size  = 100 # gb
    }
  }

  tags = [
    "airbyte",
  ]

  network_interface {
    subnetwork = google_compute_subnetwork.airbyte-subnetwork.self_link
  }

  lifecycle {
    ignore_changes = [metadata_startup_script]
  }

  metadata_startup_script = file("./init.sh")

  service_account {
    email  = google_service_account.airbyte-svc.email
    scopes = ["cloud-platform"]
  }

}

resource "google_compute_instance_group" "airbyte-instance-group" {
  name        = "airbyte-instance-group"

  instances = [
    google_compute_instance.airbyte-instance[0].id
  ]

  named_port {
    name = "api-port"
    port = "8001"
  }

  named_port {
    name = "webapp-port"
    port = "8000"
  }
}

resource "google_compute_url_map" "urlmap" {
  name        = "airbyte-url-map"
  description = "URL map for airbyte"

  default_service = google_compute_backend_service.webapp.self_link

  host_rule {
    hosts        = ["*"]
    path_matcher = "all"
  }

  path_matcher {
    name            = "all"
    default_service = google_compute_backend_service.webapp.self_link

    path_rule {
      paths   = ["/api", "/api/*"]
      service = google_compute_backend_service.api.self_link
    }
  }
}

resource "google_compute_health_check" "api" {
  name        = "api-health-check"
  description = "Health check via http"

  timeout_sec         = 10
  check_interval_sec  = 10

  http_health_check {
    port_name = "api-port"
    port_specification = "USE_NAMED_PORT"
    request_path       = "/api/v1/health"
  }
}

resource "google_compute_health_check" "webapp" {
  name        = "webapp-health-check"
  description = "Health check via http"

  timeout_sec         = 10
  check_interval_sec  = 10

  http_health_check {
    port_name = "webapp-port"
    port_specification = "USE_NAMED_PORT"
    request_path       = "/"
  }
}

resource "google_compute_backend_service" "api" {
  name        = "airbyte-api"
  description = "API Backend for airbyte"
  port_name   = "api-port"
  protocol    = "HTTP"
  timeout_sec = 20
  enable_cdn  = false

  backend {
    group = google_compute_instance_group.airbyte-instance-group.self_link
  }

  health_checks = [google_compute_health_check.api.self_link]

  depends_on = [google_compute_instance_group.airbyte-instance-group]
}

resource "google_compute_backend_service" "webapp" {
  name        = "airbyte-webapp"
  description = "webapp Backend for airbyte"
  port_name   = "webapp-port"
  protocol    = "HTTP"
  timeout_sec = 20
  enable_cdn  = false

  backend {
    group = google_compute_instance_group.airbyte-instance-group.self_link
  }

  health_checks = [google_compute_health_check.webapp.self_link]

  depends_on = [google_compute_instance_group.airbyte-instance-group]
}

resource "google_compute_global_address" "default" {
  name         = "airbyte-address"
  ip_version   = "IPV4"
  address_type = "EXTERNAL"
}

resource "google_compute_global_forwarding_rule" "https" {
  provider   = google-beta
  count      = 1
  name       = "airbyte-https-rule"
  target     = google_compute_target_https_proxy.default[0].self_link
  ip_address = google_compute_global_address.default.address
  port_range = "443"
  depends_on = [google_compute_global_address.default]
}

resource "google_compute_target_https_proxy" "default" {
  count   = 1
  name    = "airbyte-https-proxy"
  url_map = google_compute_url_map.urlmap.self_link

  ssl_certificates = [google_compute_managed_ssl_certificate.default.id]
}

resource "google_compute_managed_ssl_certificate" "default" {
  provider = google-beta

  name = "airbyte-cert"
  managed {
    domains = ["test.airbyte.io"]
  }
}
