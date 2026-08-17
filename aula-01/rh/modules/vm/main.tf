resource "google_compute_instance" "vm_instance" {
  name         = var.instance_name
  machine_type = var.machine_type
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = var.image
    }
  }

  network_interface {
    network = var.network
  }

  shielded_instance_config {
    enable_secure_boot = true
    enable_vtpm        = true
    enable_integrity_monitoring = true
  }
}
