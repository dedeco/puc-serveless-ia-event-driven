terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" { type = string }
variable "region" {
  type    = string
  default = "us-central1"
}

resource "google_service_account" "sa" {
  account_id = "aula3-step2-sa"
}

resource "google_project_iam_member" "invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.sa.email}"
}

resource "google_workflows_workflow" "wf" {
  name            = "order-retries"
  region          = var.region
  source_contents = file("workflow.yaml")
  service_account = google_service_account.sa.id
  depends_on      = [google_project_iam_member.invoker]
}

output "workflow_name" { value = google_workflows_workflow.wf.name }
