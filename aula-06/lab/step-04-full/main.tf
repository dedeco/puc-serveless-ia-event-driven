terraform {
  backend "gcs" {
    bucket = "andresousa-puc-tfstate"
    prefix = "terraform/state/aula-06/step-04"
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

# 1. Tópico Pub/Sub de falhas de build que acionará o Agente
resource "google_pubsub_topic" "build_failures" {
  name = "build-failures"
}

# 2. Banco de Dados Firestore Native (Coleção para persistência)
# ATENÇÃO: Se o banco já estiver criado no projeto, comente este recurso e use o existente.
# O banco já existe no projeto, então comentamos o recurso abaixo para evitar erros de duplicação.
# resource "google_firestore_database" "database" {
#   project                 = var.project_id
#   name                    = "(default)"
#   location_id             = "us-east1"
#   type                    = "FIRESTORE_NATIVE"
#   delete_protection_state = "DELETE_PROTECTION_DISABLED"
# }

# 3. Bucket e Código para a Função
resource "google_storage_bucket" "function_bucket" {
  name                        = "lab-aula06-src4-${random_id.bucket_suffix.hex}"
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

# 4. Service Account dedicada para o Agente Orientado a Eventos
resource "google_service_account" "agent_sa" {
  account_id   = "triage-agent-event-sa"
  display_name = "Service Account do Agente de Triagem Event-Driven"
}

# 5. Permissões IAM necessárias
# 5a. Permissão de Usuário da Vertex AI (para chamar o Gemini)
resource "google_project_iam_member" "vertex_ai_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.agent_sa.email}"
}

# 5b. Permissão de Usuário do Firestore (para gravar os relatórios)
resource "google_project_iam_member" "firestore_user" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.agent_sa.email}"
}

# 6. Cloud Function Gen 2 disparada por evento do Pub/Sub
resource "google_cloudfunctions2_function" "triage_agent" {
  name        = "triage-agent-event-driven"
  location    = var.region
  build_config {
    runtime     = "python312"
    entry_point = "triage_agent_event_driven"
    source {
      storage_source {
        bucket = google_storage_bucket.function_bucket.name
        object = google_storage_bucket_object.function_code.name
      }
    }
  }
  service_config {
    max_instance_count    = 1
    available_memory      = "512Mi"
    timeout_seconds       = 120 # loops com IA podem requerer mais tempo
    environment_variables = {
      GCP_PROJECT = var.project_id
      GCP_REGION  = var.region
    }
    service_account_email = google_service_account.agent_sa.email
  }
  event_trigger {
    event_type   = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic = google_pubsub_topic.build_failures.id
    retry_policy = "RETRY_POLICY_RETRY"
  }

  depends_on = [
    google_project_iam_member.vertex_ai_user,
    google_project_iam_member.firestore_user
    # google_firestore_database.database
  ]
}

output "topic_id" {
  value = google_pubsub_topic.build_failures.id
}
