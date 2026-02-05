import os
import google.generativeai as genai
from dotenv import load_dotenv

def verify_gemini():
    load_dotenv()
    key = os.getenv("GOOGLE_API_KEY")
    print(f"Key found: {'Yes' if key else 'No'} (Length: {len(key) if key else 0})")
    
    if not key:
        return

    genai.configure(api_key=key)
    
    print("Listing models...")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f" - {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")
        
    # Valid model names based on 2026 context
    models_to_try = ['gemini-3-pro', 'gemini-2.0-flash', 'gemini-1.5-flash-latest']
    
    # Also just try to pick the first one from list if available
    found_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    if found_models:
        print(f"Found generation models: {found_models}")
        models_to_try.insert(0, found_models[0].replace('models/', '')) # Try the first one found
    
    for model_name in models_to_try:
        print(f"Trying {model_name}...")
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hello, can you hear me?")
            print(f"SUCCESS with {model_name}: {response.text}")
            break
        except Exception as e:
            print(f"FAILED with {model_name}: {e}")

if __name__ == "__main__":
    verify_gemini()
