import requests
import google.auth
import google.auth.transport.requests

credentials, project = google.auth.default()
auth_req = google.auth.transport.requests.Request()
credentials.refresh(auth_req)
token = credentials.token

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

regions = ["us-central1"]
models = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-001",
    "gemini-1.5-flash-002",
    "gemini-2.5-flash",
    "gemini-2.5-pro"
]

for region in regions:
    for model in models:
        url = f"https://{region}-aiplatform.googleapis.com/v1/projects/andresousa-upskilling/locations/{region}/publishers/google/models/{model}:generateContent"
        data = {
            "contents": [{"role": "user", "parts": [{"text": "Hello"}]}]
        }
        try:
            response = requests.post(url, json=data, headers=headers)
            print(f"Region={region}, Model={model}, Status={response.status_code}")
            if response.status_code == 200:
                print(f"SUCCESS text: {response.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')[:100]}")
            else:
                print(f"Details: {response.json()}")
        except Exception as e:
            print(f"ERROR: {str(e)}")
print("Done.")
