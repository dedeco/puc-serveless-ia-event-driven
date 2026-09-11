terraform {
  backend "gcs" {
    bucket = "andresousa-puc-tfstate"
    prefix = "terraform/state/aula-06/step-03"
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

# 1. Bucket e Código para a Função
resource "google_storage_bucket" "function_bucket" {
  name                        = "lab-aula06-src3-${random_id.bucket_suffix.hex}"
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

# 2. Service Account dedicada para o Agente de Triagem ReAct
resource "google_service_account" "agent_sa" {
  account_id   = "triage-agent-react-sa"
  display_name = "Service Account do Agente de Triagem de DevOps ReAct"
}

# 3. Permissões IAM necessárias (Vertex AI User)
resource "google_project_iam_member" "vertex_ai_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.agent_sa.email}"
}

# 4. Cloud Function Gen 2 HTTP
resource "google_cloudfunctions2_function" "triage_agent" {
  name        = "triage-agent-react"
  location    = var.region
  build_config {
    runtime     = "python312"
    entry_point = "triage_agent"
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
    timeout_seconds       = 60
    environment_variables = {
      GCP_PROJECT = var.project_id
      GCP_REGION  = var.region
    }
    service_account_email = google_service_account.agent_sa.email
  }

  depends_on = [
    google_project_iam_member.vertex_ai_user
  ]
}

output "function_url" {
  value = google_cloudfunctions2_function.triage_agent.service_config[0].uri
}
