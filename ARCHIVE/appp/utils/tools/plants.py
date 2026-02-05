import google.generativeai as genai
import os

# this file houses the function to generate a plant related response and give those insights from the image if the image analysis deems it to most valuable for plant insights
# it sends the image again and user context for response generation. This allows for complex insights to be generated in a personalized way.

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

def generate_plant_response(response_text, spoken_text, base64_image):
    text_prompt = f"""
    Instructions: Planty adopts a friendly and casual tone in its interactions, making plant care advice feel approachable and easy to understand. This approachable demeanor helps in demystifying complex gardening topics and makes the guidance feel more like a conversation with a knowledgeable friend. Planty's friendly tone is especially beneficial for novice gardeners who might be intimidated by technical jargon. The goal is to make everyone, regardless of their gardening experience, feel comfortable and confident in seeking and applying Planty's advice.

    Following the instructions on how to act, give some insights based on the picture of the plant. Be super smart and friendly. Your response is going straight to the user who took the pic.
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
