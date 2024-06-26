import google.generativeai as genai
import os

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

def generate_food_response(response_text, spoken_text):
    text_prompt = f"""
    Here is the spoken text provided by the user for additional context:
    {spoken_text}
    
    Here is the description you should use for your analysis:
    {response_text}

    Based on the provided description and material info, conduct a detailed analysis of the food storage or preparation area. Your analysis should include the following:

    1. Ingredient Assessment: Identify and evaluate the condition of the ingredients present in the storage area. Discuss their freshness, spoilage indicators, and optimal storage methods to extend their shelf life.

    2. Storage Efficiency: Analyze the efficiency of the current storage setup, including organization, temperature control, and humidity levels. Suggest improvements to enhance the preservation of the ingredients and prevent food waste.

    3. Nutritional Insights: Provide a nutritional breakdown of the visible ingredients, highlighting their health benefits and potential dietary contributions. Suggest balanced meal ideas or recipes based on the available ingredients.

    4. Food Safety: Address any food safety concerns, such as cross-contamination risks, proper labeling, and safe handling practices. Recommend best practices to ensure the stored food remains safe for consumption.

    5. Sustainability Practices: Discuss sustainable practices that can be implemented in the food storage area, such as using eco-friendly containers, reducing plastic use, and composting food scraps. Provide actionable tips for creating a more sustainable kitchen environment.

    Ensure that your response is comprehensive, practical, and tailored to the specific details provided in the description and material info.
    Limit each response to 200 words max. 
"""


    text_model = genai.GenerativeModel(
        model_name="gemini-1.0-pro",
        generation_config={
            "temperature": 0.8,
            "top_p": 1,
            "top_k": 40,
            "max_output_tokens": 2048,
        },
        safety_settings=[{"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}]
    )

    text_response = text_model.generate_content([text_prompt])
    text_analysis_result = text_response.text

    return {
        'result': text_analysis_result
    }
