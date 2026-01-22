import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY not found in .env file")
    exit()

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
response = requests.get(url)

if response.status_code == 200:
    print("✅ SUCCESS! Here are your available models:\n")
    models = response.json().get('models', [])
    for m in models:
        # We only care about models that support 'generateContent'
        if "generateContent" in m.get("supportedGenerationMethods", []):
            print(f"  • {m['name'].replace('models/', '')}")
else:
    print(f"❌ Failed to list models. Status: {response.status_code}")
    print(response.text)