terraform {
  backend "gcs" {
    bucket = "andresousa-puc-tfstate"
    prefix = "terraform/state/rh/dev"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

module "vm_factory" {
  source   = "../../modules/vm"
  for_each = var.vms

  instance_name = each.key
  machine_type  = each.value.machine_type
  zone          = each.value.zone
  image         = each.value.image
  network       = google_compute_network.vpc_network.name
}
