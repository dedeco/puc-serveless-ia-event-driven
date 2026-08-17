variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "us-central1"
}

variable "vms" {
  description = "Map of VM instances to create"
  type = map(object({
    machine_type = optional(string, "e2-medium")
    zone         = optional(string, "us-central1-a")
    image        = optional(string, "debian-cloud/debian-11")
  }))
}
