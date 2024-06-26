import google.generativeai as genai
import os

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

def generate_composting_response(response_text, spoken_text):
    text_prompt = f"""
    Here is the spoken text provided by the user for additional context:
    {spoken_text}
    
    Here is the description you should use for your analysis:
    {response_text}

    Based on the provided description and material info, analyze the suitability of the materials for composting. Your analysis should include the following:

    1. Breakdown Potential: Evaluate the decomposition rate of the materials, considering factors such as moisture content, carbon to nitrogen ratio, and particle size. Provide a detailed assessment of each material's compostability.

    2. Optimal Conditions: Describe the optimal conditions for composting the materials, including the necessary temperature range, aeration requirements, and moisture levels. Suggest any modifications needed to create these conditions if they are not already present.

    3. Potential Challenges: Identify any potential challenges or issues that could arise during the composting process, such as pest attraction, unpleasant odors, or material contamination. Offer solutions or preventive measures for each identified challenge.

    4. End Product Quality: Discuss the expected quality of the compost produced from these materials. Include insights into nutrient content, texture, and potential uses for the finished compost in gardening or agriculture.

    5. Sustainability Insights: Highlight any sustainability benefits of composting these materials, such as reducing landfill waste, enhancing soil health, and lowering greenhouse gas emissions. Provide a comprehensive analysis of the environmental impact of composting these materials compared to alternative disposal methods.

    Ensure that your response is detailed, scientifically accurate, and includes practical recommendations based on the provided description and material info.
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
