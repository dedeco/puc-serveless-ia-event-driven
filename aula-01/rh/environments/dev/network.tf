resource "google_compute_network" "vpc_network" {
  name                    = "vpc-rh-dev"
  auto_create_subnetworks = true
}
