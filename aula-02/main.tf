terraform {
  backend "gcs" {
    bucket = "andresousa-puc-tfstate"
    prefix = "terraform/state/aula-02"
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

variable "project_id" {
  description = "The ID of the project to deploy to"
  type        = string
}

variable "region" {
  description = "The region to deploy to"
  type        = string
  default     = "us-central1"
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# 1. Pub/Sub Topics
resource "google_pubsub_topic" "orders" {
  name = "orders"
}

resource "google_pubsub_topic" "payments" {
  name = "payments"
}

# 2. Cloud Storage Bucket for function code
resource "google_storage_bucket" "function_bucket" {
  name                        = "aula02-function-source-${random_id.bucket_suffix.hex}"
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = true
}

# 3. Firestore Database
resource "google_firestore_database" "database" {
  project     = var.project_id
  name        = "(default)"
  location_id = "us-east1" 
  type        = "FIRESTORE_NATIVE"
  
  delete_protection_state = "DELETE_PROTECTION_DISABLED"
}

# 4. Zip and Upload the source code
data "archive_file" "function_zip" {
  type        = "zip"
  source_dir  = "${path.module}/src"
  output_path = "${path.module}/function-source.zip"
}

resource "google_storage_bucket_object" "function_code" {
  name   = "function-source-${data.archive_file.function_zip.output_md5}.zip"
  bucket = google_storage_bucket.function_bucket.name
  source = data.archive_file.function_zip.output_path
}

# 5. Cloud Function 1: Inventory Service (Reacts to 'orders')
resource "google_cloudfunctions2_function" "inventory" {
  name        = "inventory-service"
  location    = var.region
  description = "Serviço de Inventário (Aula 2)"

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
    max_instance_count = 1
    available_memory   = "256Mi"
    timeout_seconds    = 60
    environment_variables = {
      GCP_PROJECT = var.project_id
    }
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic   = google_pubsub_topic.orders.id
    retry_policy   = "RETRY_POLICY_RETRY"
  }
}

# 6. Cloud Function 2: Payment Service (Reacts to 'orders')
resource "google_cloudfunctions2_function" "payment" {
  name        = "payment-service"
  location    = var.region
  description = "Serviço de Pagamento (Aula 2)"

  build_config {
    runtime     = "python312"
    entry_point = "payment_service"
    source {
      storage_source {
        bucket = google_storage_bucket.function_bucket.name
        object = google_storage_bucket_object.function_code.name
      }
    }
  }

  service_config {
    max_instance_count = 1
    available_memory   = "256Mi"
    timeout_seconds    = 60
    environment_variables = {
      GCP_PROJECT = var.project_id
    }
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic   = google_pubsub_topic.orders.id
    retry_policy   = "RETRY_POLICY_RETRY"
  }
}

# 7. Cloud Function 3: Shipping Service (Reacts to 'payments')
resource "google_cloudfunctions2_function" "shipping" {
  name        = "shipping-service"
  location    = var.region
  description = "Serviço de Logística (Aula 2)"

  build_config {
    runtime     = "python312"
    entry_point = "shipping_service"
    source {
      storage_source {
        bucket = google_storage_bucket.function_bucket.name
        object = google_storage_bucket_object.function_code.name
      }
    }
  }

  service_config {
    max_instance_count = 1
    available_memory   = "256Mi"
    timeout_seconds    = 60
    environment_variables = {
      GCP_PROJECT = var.project_id
    }
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic   = google_pubsub_topic.payments.id
    retry_policy   = "RETRY_POLICY_RETRY"
  }
}

# 8. Cloud Function 4: Read Model Simulator (Reacts to 'orders')
resource "google_cloudfunctions2_function" "read_model" {
  name        = "read-model-simulator"
  location    = var.region
  description = "Consolidador de Visão (Aula 2)"

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
    max_instance_count = 1
    available_memory   = "256Mi"
    timeout_seconds    = 60
    environment_variables = {
      GCP_PROJECT = var.project_id
    }
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic   = google_pubsub_topic.orders.id
    retry_policy   = "RETRY_POLICY_RETRY"
  }
}

output "topic_orders" {
  value = google_pubsub_topic.orders.name
}

output "topic_payments" {
  value = google_pubsub_topic.payments.name
}
