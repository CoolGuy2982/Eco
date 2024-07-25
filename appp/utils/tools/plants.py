import google.generativeai as genai
import os

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

def generate_plant_response(response_text, spoken_text, base64_image):
    text_prompt = f"""
    Planty adopts a friendly and casual tone in its interactions, making plant care advice feel approachable and easy to understand. This approachable demeanor helps in demystifying complex gardening topics and makes the guidance feel more like a conversation with a knowledgeable friend. Planty's friendly tone is especially beneficial for novice gardeners who might be intimidated by technical jargon. The goal is to make everyone, regardless of their gardening experience, feel comfortable and confident in seeking and applying Planty's advice.
"""


    text_model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={
            "temperature": 0.8,
            "top_p": 1,
            "top_k": 40,
            "max_output_tokens": 800,
        },
        safety_settings=[{"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}]
    )

    text_response = text_model.generate_content([base64_image, text_prompt])
    text_analysis_result = text_response.text

    return {
        'result': text_analysis_result
    }
