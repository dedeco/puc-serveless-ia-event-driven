terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = "andresousa-puc"
  region  = "us-central1"
}

# Conexão manual do GitHub via Cloud Build v2 (importada para o Terraform)
resource "google_cloudbuildv2_connection" "aula_05" {
  location = "africa-south1"
  name     = "aula-05"

  github_config {
    app_installation_id = 34396305
    authorizer_credential {
      oauth_token_secret_version = "projects/andresousa-puc/secrets/aula-05-github-oauthtoken-21a6a3/versions/latest"
    }
  }
}

# Repositório conectado através do Cloud Build v2
resource "google_cloudbuildv2_repository" "aula_05_repo" {
  location          = "africa-south1"
  name              = "puc-serveless-ia-event-driven"
  parent_connection = google_cloudbuildv2_connection.aula_05.id
  remote_uri        = "https://github.com/dedeco/puc-serveless-ia-event-driven.git"
}

# Gatilho do Cloud Build conectado ao repositório do GitHub (branch main)
resource "google_cloudbuild_trigger" "main_trigger" {
  name        = "calculator-main-trigger"
  description = "Trigger para a branch main do repositório da Aula 05 no GitHub"
  location    = "africa-south1"

  repository_event_config {
    repository = google_cloudbuildv2_repository.aula_05_repo.id
    push {
      branch = "^main$"
    }
  }

  filename = "aula-05/calculator-service/cloudbuild.yaml"
}
