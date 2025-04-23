import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
print(f"Using API key: {GEMINI_API_KEY[:5]}...{GEMINI_API_KEY[-4:]}")

try:
    genai.configure(api_key=GEMINI_API_KEY)
    
    # List available models
    print("Listing available models:")
    for model in genai.list_models():
        print(f"- {model.name}")
    
    # Use gemini-1.0-pro or gemini-1.5-pro based on availability
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Test with a simple prompt
    response = model.generate_content("Say hello world")
    print("API connection successful!")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error connecting to Gemini API: {str(e)}") 