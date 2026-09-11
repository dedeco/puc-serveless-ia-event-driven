import functions_framework
import json
import os
from google import genai
from google.genai import types

PROJECT_ID = os.environ.get("GCP_PROJECT")
REGION = os.environ.get("GCP_REGION", "us-central1")

# Inicializa o cliente do google-genai para Vertex AI
# A Service Account anexada à Cloud Function proverá a autenticação automaticamente.
client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location="global"
)

@functions_framework.http
def triage_agent(request):
    """
    HTTP Cloud Function que recebe um prompt no payload JSON
    e retorna a resposta gerada pelo Gemini (Vertex AI).
    """
    if request.method == "OPTIONS":
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Max-Age": "3600"
        }
        return ("", 204, headers)

    headers = {"Access-Control-Allow-Origin": "*"}

    try:
        request_json = request.get_json(silent=True)
        if not request_json or "prompt" not in request_json:
            return (json.dumps({"error": "O campo 'prompt' e obrigatorio no JSON."}), 400, headers)

        prompt = request_json["prompt"]
        model = request_json.get("model", "gemini-1.5-flash")
        print(f"Recebido prompt: {prompt}, model: {model}")
        
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)]
            )
        ]
        
        # Tools do snippet do Agent Studio
        tools = [
            types.Tool(google_search=types.GoogleSearch()),
            types.Tool(google_maps=types.GoogleMaps()),
        ]
        
        tool_config = types.ToolConfig(
            retrieval_config=types.RetrievalConfig()
        )

        generate_content_config = types.GenerateContentConfig(
            max_output_tokens=65535,
            safety_settings=[
                types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
                types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
                types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
                types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF")
            ],
            tools=tools,
            tool_config=tool_config,
            thinking_config=types.ThinkingConfig(
                thinking_level="MEDIUM"
            ),
        )

        # Gera o conteúdo
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=generate_content_config,
        )
        
        return (json.dumps({
            "prompt": prompt,
            "response": response.text
        }, ensure_ascii=False), 200, headers)

    except Exception as e:
        print(f"Erro ao processar a requisição: {str(e)}")
        return (json.dumps({"error": str(e)}), 500, headers)
