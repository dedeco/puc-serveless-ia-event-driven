variable "instance_name" {
  description = "Name of the VM instance"
  type        = string
}

variable "machine_type" {
  description = "Machine type for the VM"
  type        = string
  default     = "e2-medium"
}

variable "zone" {
  description = "GCP zone"
  type        = string
}

variable "image" {
  description = "Boot image for the VM"
  type        = string
  default     = "debian-cloud/debian-11"
}

variable "network" {
  description = "Network to attach the VM to"
  type        = string
  default     = "default"
}
