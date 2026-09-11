#!/bin/bash
set -eo pipefail

PROJECT_ID="andresousa-puc"
PROJECT_NUMBER="575401317367"
REGION="us-central1"

echo "==============================================="
echo "Initializing infrastructure setup for Aula 05"
echo "==============================================="

# 1. Enable Google Cloud APIs
echo "Enabling necessary APIs..."
gcloud services enable \
  secretmanager.googleapis.com \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  cloudfunctions.googleapis.com \
  artifactregistry.googleapis.com \
  --project="${PROJECT_ID}"

# 2. Create Service Account for the Function
SA_NAME="calculator-service-sa"
SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

if ! gcloud iam service-accounts describe "${SA_EMAIL}" --project="${PROJECT_ID}" &>/dev/null; then
  echo "Creating service account: ${SA_EMAIL}..."
  gcloud iam service-accounts create "${SA_NAME}" \
    --description="Service account for calculator service" \
    --display-name="Calculator Service SA" \
    --project="${PROJECT_ID}"
else
  echo "Service account ${SA_EMAIL} already exists."
fi

# 3. Create Secret in Secret Manager
SECRET_NAME="calculator-secret"

if ! gcloud secrets describe "${SECRET_NAME}" --project="${PROJECT_ID}" &>/dev/null; then
  echo "Creating secret: ${SECRET_NAME}..."
  gcloud secrets create "${SECRET_NAME}" \
    --replication-policy="automatic" \
    --project="${PROJECT_ID}"
  
  echo "Adding first version of the secret..."
  echo -n "Chave-Super-Secreta-Aula-05" | gcloud secrets versions add "${SECRET_NAME}" --data-file=- --project="${PROJECT_ID}"
else
  echo "Secret ${SECRET_NAME} already exists."
fi

# 4. Grant Secret Access to the Service Account
echo "Granting secretAccessor role on ${SECRET_NAME} to ${SA_EMAIL}..."
gcloud secrets add-iam-policy-binding "${SECRET_NAME}" \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/secretmanager.secretAccessor" \
  --project="${PROJECT_ID}"

# 5. Grant Permissions to Cloud Build Service Account
CB_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

echo "Granting Cloud Functions Developer role on project to Cloud Build..."
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${CB_SA}" \
  --role="roles/cloudfunctions.developer"

echo "Granting Cloud Run Admin role on project to Cloud Build..."
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${CB_SA}" \
  --role="roles/run.admin"

echo "Granting Artifact Registry Admin role on project to Cloud Build..."
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${CB_SA}" \
  --role="roles/artifactregistry.admin"

echo "Granting Service Account User role to Cloud Build on our runtime Service Account..."
gcloud iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
  --member="serviceAccount:${CB_SA}" \
  --role="roles/iam.serviceAccountUser" \
  --project="${PROJECT_ID}"

# Wait, Cloud Build also needs Service Account User on default compute service account if cloud function gen2 uses it (as fallback/underlying)
echo "Granting Service Account User role on compute default service account to Cloud Build..."
gcloud iam service-accounts add-iam-policy-binding "${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --member="serviceAccount:${CB_SA}" \
  --role="roles/iam.serviceAccountUser" \
  --project="${PROJECT_ID}"

# 6. Attempt to create Cloud Build Trigger
echo "Attempting to create Cloud Build trigger for GitHub repository..."
if ! gcloud builds triggers describe "calculator-trigger" --region="${REGION}" --project="${PROJECT_ID}" &>/dev/null; then
  gcloud builds triggers create github \
    --name="calculator-trigger" \
    --repo-owner="dedeco" \
    --repo-name="puc-serveless-ia-event-driven" \
    --branch-pattern="main" \
    --build-config="cloudbuild.yaml" \
    --region="${REGION}" \
    --project="${PROJECT_ID}" || echo "Warning: Could not create GitHub trigger because GitHub repo connection is manual or not pre-authenticated. This is expected if the connection is configured in the console."
else
  echo "Cloud Build trigger calculator-trigger already exists."
fi

echo "==============================================="
echo "Infrastructure Setup Completed Successfully!"
echo "==============================================="
