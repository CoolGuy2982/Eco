import google.generativeai as genai
import os

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

def generate_eco_response(response_text, spoken_text):
    text_prompt = f"""
    Here is the spoken text provided by the user for additional context:
    {spoken_text}
    
    Here is the description you should use for your analysis:
    {response_text}

    Based on the provided description and material info, perform an in-depth analysis of the environmental scene depicted. Your analysis should include the following:

    1. Ecological Assessment: Evaluate the ecological health of the environment shown, considering biodiversity, presence of native species, and any signs of ecological stress or disturbance. Provide a detailed assessment of the current state of the ecosystem.

    2. Environmental Challenges: Identify any environmental challenges or threats present in the scene, such as pollution, habitat loss, invasive species, or climate change impacts. Discuss the potential long-term effects of these challenges on the ecosystem.

    3. Conservation Recommendations: Propose conservation strategies or interventions to address the identified challenges. Include specific actions that can be taken by individuals, communities, or organizations to support the preservation and restoration of the environment.

    4. Sustainability Opportunities: Highlight opportunities for promoting sustainability within the depicted environment, such as implementing renewable energy sources, supporting local wildlife, or engaging in community-driven environmental initiatives.

    5. Educational Insights: Provide educational insights about the depicted environment, including unique features, historical significance, and the role of the ecosystem in the broader environmental context. Offer suggestions for further learning and engagement with environmental issues.

    Ensure that your response is thorough, scientifically grounded, and provides practical recommendations based on the provided description and material info.
    Limit each response to 200 words max.
"""


    text_model = genai.GenerativeModel(
        model_name="gemini-1.0-pro",
        generation_config={
            "temperature": 0.4,
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
