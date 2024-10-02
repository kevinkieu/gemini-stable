import google.generativeai as genai
from config import GOOGLE_API_KEY, MODEL_NAME, TEMPERATURE, TOP_P, TOP_K, MAX_TOKENS
from PIL import Image

genai.configure(api_key=GOOGLE_API_KEY)
text_model = genai.GenerativeModel(MODEL_NAME)
vision_model = genai.GenerativeModel('gemini-1.5-flash')

def generate_text(prompt, system_instruction, history):
    messages = [
        {"role": "user", "parts": [{"text": system_instruction}]},
        {"role": "model", "parts": [{"text": "Understood. I will act as a helpful AI assistant."}]}
    ]
    for msg in history:
        role = "user" if msg["role"] == "user" else "model"
        messages.append({"role": role, "parts": [{"text": msg["content"]}]})
    messages.append({"role": "user", "parts": [{"text": prompt}]})
    
    response = text_model.generate_content(
        messages,
        generation_config=genai.types.GenerationConfig(
            temperature=TEMPERATURE,
            top_p=TOP_P,
            top_k=TOP_K,
            max_output_tokens=MAX_TOKENS,
        ),
        stream=True
    )
    return response

def analyze_image(image: Image, prompt: str):
    response = vision_model.generate_content([prompt, image], stream=True)
    return response