import google.generativeai as genai
import os

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

def generate_nature_response(response_text, spoken_text):
    text_prompt = f"""
    Here is the spoken text provided by the user for additional context:
    {spoken_text}
    
    Here is the description you should use for your analysis:
    {response_text}

    Based on the provided description and material info, conduct a comprehensive analysis of the natural environment depicted. Your analysis should include the following:

    1. Biodiversity Evaluation: Assess the biodiversity present in the scene, identifying key species of plants and animals. Discuss their roles within the ecosystem and any notable interactions or behaviors observed.

    2. Environmental Health: Evaluate the health of the natural environment, noting any signs of ecological balance or imbalance. Consider factors such as plant health, water quality, soil condition, and the presence of natural or human-induced disturbances.

    3. Conservation Significance: Discuss the conservation significance of the natural environment, highlighting any protected areas, endangered species, or unique ecological features. Provide recommendations for conserving and enhancing the ecological value of the area.

    4. Ecological Interactions: Describe the ecological interactions observed in the scene, such as predator-prey relationships, pollination, or nutrient cycling. Explain how these interactions contribute to the overall health and stability of the ecosystem.

    5. Human Impact: Analyze the potential impact of human activities on the natural environment, including positive contributions and negative effects. Suggest strategies for minimizing harmful impacts and promoting sustainable interactions with nature.

    Ensure that your response is detailed, ecologically sound, and provides actionable insights based on the provided description and material info.
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
