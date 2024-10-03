import google.generativeai as genai
from config import GOOGLE_API_KEY, MODEL_NAME, TEMPERATURE, TOP_P, TOP_K, MAX_TOKENS, SAFETY_SETTINGS
from PIL import Image
import pdfplumber

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
        safety_settings=SAFETY_SETTINGS,
        stream=True
    )
    
    for chunk in response:
        if hasattr(chunk, 'text'):
            yield chunk.text
        elif hasattr(chunk, 'parts'):
            for part in chunk.parts:
                if hasattr(part, 'text'):
                    yield part.text

def analyze_image(image: Image, prompt: str):
    response = vision_model.generate_content([prompt, image], safety_settings=SAFETY_SETTINGS, stream=True)
    for chunk in response:
        if hasattr(chunk, 'text'):
            yield chunk.text
        elif hasattr(chunk, 'parts'):
            for part in chunk.parts:
                if hasattr(part, 'text'):
                    yield part.text

def process_pdf(file_path, prompt):
    try:
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        
        max_chars = 10000
        if len(text) > max_chars:
            text = text[:max_chars] + "...(truncated)"

        messages = [
            {"role": "user", "parts": [{"text": f"Analyze the following PDF content:\n\n{text}\n\nUser's request: {prompt}"}]},
        ]

        response = text_model.generate_content(
            messages,
            generation_config=genai.types.GenerationConfig(
                temperature=TEMPERATURE,
                top_p=TOP_P,
                top_k=TOP_K,
                max_output_tokens=MAX_TOKENS,
            ),
            safety_settings=SAFETY_SETTINGS,
            stream=True
        )
        
        for chunk in response:
            if hasattr(chunk, 'text'):
                yield chunk.text
            elif hasattr(chunk, 'parts'):
                for part in chunk.parts:
                    if hasattr(part, 'text'):
                        yield part.text
    except Exception as e:
        raise Exception(f"Error processing PDF: {str(e)}")