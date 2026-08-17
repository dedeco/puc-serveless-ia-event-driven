# Calculator Service

A basic calculator service built with Flask.

## Local Setup

1. Create a virtual environment:
   ```bash
   uv venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   python main.py
   ```

## API Usage

### Calculate
- **Endpoint:** `/calculate`
- **Method:** `POST`
- **Body:**
  ```json
  {
    "operation": "add",
    "a": 10,
    "b": 5
  }
  ```
- **Operations:** `add`, `subtract`, `multiply`, `divide`

## Deployment to Cloud Functions

To deploy this as a Google Cloud Function:

```bash
gcloud functions deploy calculator-service \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point calculate
```
*(Note: You might need to adjust `main.py` to use `functions-framework` if deploying specifically to GCF 2nd gen, but Flask apps are directly supported in many serverless platforms like Cloud Run.)*
