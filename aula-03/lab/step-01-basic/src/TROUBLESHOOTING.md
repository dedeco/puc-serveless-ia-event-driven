# Troubleshooting: Cloud Run 503 Service Unavailable

## Issue
The workflow `order-basic` was failing with a `503 Service Unavailable` error when calling the `/reserve` endpoint of the Cloud Run service.

## Diagnosis
1.  **Manual Test:** A manual `curl` request to the `/reserve` endpoint also returned `503 Service Unavailable`, confirming the issue was with the service itself.
2.  **Log Inspection:** Checking the Cloud Run logs (`gcloud logging read ...`) revealed that the service instances were failing to start.
3.  **Error Identification:** The build logs (via `gcloud builds log ...`) showed that the build process failed because the Python version `3.11` specified in `.python-version` was not supported by the current buildpacks:
    ```
    Step #1 - "build": invalid Python version specified: failed to resolve version matching: 3.11 ...
    ```

## Resolution
1.  **Update Python Version:** Updated `.python-version` from `3.11` to `3.13` to match the versions supported by the buildpacks.
2.  **Re-deploy Service:** Re-deployed the Cloud Run service from source to trigger a new build with the updated configuration:
    ```bash
    gcloud run deploy simulator-step1 --source=src --platform managed --region us-central1
    ```

## Verification
1.  **Endpoint Test:** A manual `curl` request now returns `HTTP 200 OK`.
2.  **Workflow Execution:** The workflow `order-basic` now completes successfully.
