terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

terraform {
  backend "gcs" {
    bucket = "andresousa-puc-tfstate"
    prefix = "terraform/state/aula-02/step-01"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {}
variable "region" { default = "us-central1" }

# STEP 1: CRIANDO OS TÓPICOS
resource "google_pubsub_topic" "orders" {
  name = "orders"
}

resource "google_pubsub_topic" "payments" {
  name = "payments"
}

output "topic_orders" { value = google_pubsub_topic.orders.name }
output "topic_payments" { value = google_pubsub_topic.payments.name }
