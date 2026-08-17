terraform {
  backend "gcs" {
    bucket = "andresousa-puc-tfstate"
    prefix = "terraform/state/aula-02/step-02"
  }
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {}
variable "region" { default = "us-central1" }

resource "random_id" "bucket_suffix" { byte_length = 4 }

# 1. Tópico 'orders'
resource "google_pubsub_topic" "orders" {
  name = "orders"
}

# 2. Firestore para persistência (Obrigatório para Inventory/ReadModel)
resource "google_firestore_database" "database" {
  project     = var.project_id
  name        = "(default)"
  location_id = "us-east1" 
  type        = "FIRESTORE_NATIVE"
  delete_protection_state = "DELETE_PROTECTION_DISABLED"
}

# 3. Bucket e Código das Funções
resource "google_storage_bucket" "function_bucket" {
  name                        = "lab-aula02-src-${random_id.bucket_suffix.hex}"
  location                    = var.region
  force_destroy               = true
  uniform_bucket_level_access = true
}

data "archive_file" "function_zip" {
  type        = "zip"
  source_dir  = "${path.module}/src"
  output_path = "${path.module}/function-source.zip"
}

resource "google_storage_bucket_object" "function_code" {
  name   = "source-${data.archive_file.function_zip.output_md5}.zip"
  bucket = google_storage_bucket.function_bucket.name
  source = data.archive_file.function_zip.output_path
}

# 4. Cloud Function: Inventory Service (Fan-out 1)
resource "google_cloudfunctions2_function" "inventory" {
  name        = "inventory-service"
  location    = var.region
  build_config {
    runtime     = "python312"
    entry_point = "inventory_service"
    source {
      storage_source {
        bucket = google_storage_bucket.function_bucket.name
        object = google_storage_bucket_object.function_code.name
      }
    }
  }
  service_config {
    max_instance_count    = 1
    available_memory      = "256Mi"
    environment_variables = { GCP_PROJECT = var.project_id }
  }
  event_trigger {
    event_type = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic = google_pubsub_topic.orders.id
    retry_policy = "RETRY_POLICY_RETRY"
  }
}

# 5. Cloud Function: Read Model Simulator (Fan-out 2)
resource "google_cloudfunctions2_function" "read_model" {
  name        = "read-model-simulator"
  location    = var.region
  build_config {
    runtime     = "python312"
    entry_point = "read_model_simulator"
    source {
      storage_source {
        bucket = google_storage_bucket.function_bucket.name
        object = google_storage_bucket_object.function_code.name
      }
    }
  }
  service_config {
    max_instance_count    = 1
    available_memory      = "256Mi"
    environment_variables = { GCP_PROJECT = var.project_id }
  }
  event_trigger {
    event_type = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic = google_pubsub_topic.orders.id
    retry_policy = "RETRY_POLICY_RETRY"
  }
}
