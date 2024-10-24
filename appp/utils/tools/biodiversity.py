import google.generativeai as genai
import os

# this file houses the function to generate a biodiversity related response and give those insights from the image if the image analysis deems it to most valuable for biodiversity insights
# it sends the image again and user context for response generation. This allows for complex insights to be generated in a personalized way.
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

def generate_biodiversity_response(response_text, spoken_text, base64_image):
    text_prompt = f"""
Give biodiversity insights using a lot of technical words based on the picture but also explain it in case they are a novice. 
Make response casual and natural conversation, not bullet points. 
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
