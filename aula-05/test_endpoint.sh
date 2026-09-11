#!/bin/bash
set -e

echo "Fetching Google Cloud auth identity token..."
TOKEN=$(gcloud auth print-identity-token)

URL="https://calculator-service-aula5-uucgfw647q-uc.a.run.app"

echo "Sending POST request to ${URL}..."
curl -i -X POST "${URL}" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"operation": "add", "a": 10, "b": 5}'

echo ""
echo "Test completed successfully!"
