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
  count        = 1
  name        = "airbyte-instance-group"

  instances = [
    google_compute_instance.airbyte-instance[0].id
  ]
}
