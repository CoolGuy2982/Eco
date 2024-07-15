import os
import base64
import google.generativeai as genai
import json
from .tools.nature import generate_nature_response
from .tools.food import generate_food_response
from .tools.recycling import generate_recycling_response
from .tools.greenwashing import generate_greenwashing_response
from .tools.composting import generate_composting_response
from .tools.general_eco import generate_eco_response

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

def analyze_image(base64_image, spoken_text):
    img_data = base64.b64decode(base64_image)

    try:
        image_model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={
                "temperature": 0.4,
                "top_p": 1,
                "top_k": 32,
                "max_output_tokens": 4096,
                "response_mime_type": "application/json"
            },
            safety_settings=[{"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}]
        )

        image_parts = [{"mime_type": "image/jpeg", "data": img_data}]
        image_prompt_parts = [
            image_parts[0],
            f"""
            Analyze the image in detail and provide a comprehensive description without mentioning people or humans. If there is a red box in the image, the user emphasises on what's generally in that red box. Follow these steps:

            1. Main Purpose Identification: Determine the main purpose of the image by analyzing its contents and considering the user query: "{spoken_text}". Use these observations to select the most fitting tool:
            - Nature (Tool A): Choose this if the image prominently features nature and natural environments such as forests, rivers, mountains, or wildlife. Look for elements that emphasize ecological dynamics, like interactions among animals, plant growth, or seasonal changes in landscapes.
            - Recycling (Tool B): Choose this if the image features any item/product in a home or outdoor setting or generally looks like trash. This could be any type of item/product.
            - Greenwashing (Tool C): Opt for this if the image shows products in a commercial setting, like a store, being advertised with environmental claims. Look for labels like "eco-friendly," "sustainable," "green," "ethical," "organic," or "natural" on packaging, particularly in contexts that might suggest exaggerated or misleading claims.
            - Composting (Tool D): Use this if the image includes biodegradable materials suitable for composting. This might include food scraps, yard debris like leaves and grass, or other organic waste clearly intended to decompose in a compost setting.
            - Food (Tool E): Choose this tool if the image displays food storage or preparation areas such as kitchens, pantries, or refrigerators, featuring ingredients either being used for cooking or stored for future use.
            - General Specialist (Tool F): Use this tool if the image doesn't fit any of the other categories even vaguely. This is for ambiguous queries where physical items are generally tools B & C, not F. YOU WILL RARELY CHOOSE THIS TOOL.

            Hints: Generally, the item in question if there is one will be in the center of the frame.
            
            2. Detailed Description: Based on the selected tool, provide a detailed description focusing on the following aspects:
            - Nature (Tool A):
                - Identification: Identify the primary object or scene, including specific species of plants and animals.
                - Condition: Note any visible features such as health, growth stage, or signs of disease.
                - Composition: Describe key characteristics of the species, including size, color, and distinctive features.
                - Contextual Clues: Consider surrounding elements that provide ecological context, such as other species or environmental conditions.
                - Special Characteristics: Highlight unique features relevant to biodiversity insights, like habitat details or ecological interactions.
            - Recycling (Tool B):
                - Identification: Identify the primary item, including specific types like type 3 plastic or aluminum Coca-Cola can.
                - Condition: Note any visible features such as contamination or damage.
                - Text Details: Note any text on the item related to the material of the packaging.
                - Composition: Describe materials or components of the item, including recyclability information.
                - Contextual Clues: Consider surrounding items that provide context, such as packaging or location.
                - Special Characteristics: Highlight any greenwashing aspects or other sustainability insights, including label information.
            - Greenwashing (Tool C):
                - Identification: Identify the primary item, including specific types like type 3 plastic or aluminum Coca-Cola can.
                - Condition: Note any visible features such as contamination or damage.
                - Composition: Describe materials or components of the item, including recyclability information.
                - Contextual Clues: Consider surrounding items that provide context, such as packaging or location.
                - Special Characteristics: Highlight any greenwashing aspects or other sustainability insights, including label information.
                - Text Details: Transcribe all visible text on the packaging/product.
            - Composting (Tool D):
                - Identification: Identify the primary compostable item, such as vegetable scraps or garden waste.
                - Condition: Note any visible features such as freshness or decomposition.
                - Composition: Describe the organic material and its compostability.
                - Contextual Clues: Consider surrounding elements that provide context, such as other compostable items or compost bins.
                - Special Characteristics: Highlight any signs of successful or unsuccessful composting.
            - Food (Tool E):
                - Identification: Identify the ingredients shown in a fridge, pantry, or the frame.
                - Condition: Note any visible features such as freshness or spoilage.
                - Quantity: List the general quantities of the ingredients.
                - Composition: List all the ingredients and their quantities if visible.
                - Contextual Clues: Consider surrounding items that provide culinary context, such as other ingredients or kitchen tools.
            - General Specialist (Tool F):
                - Identification: Identify the primary environmental query or issue.
                - Condition: Note any visible features relevant to the query.
                - Composition: Describe materials or components related to the query.
                - Contextual Clues: Consider surrounding elements that provide context.
                - Special Characteristics: Highlight any unique features relevant to the environmental query.

            3. JSON Response: Format the response as follows (example):
            {{
                "Response": "<detailed description>",
                "Text_Tool": "A",
                "Material": "if you selected tool B <add the material of the general item if applicable (e.g., Plastic)>"
            }}
            """,
            "\n"
        ]

        image_response = image_model.generate_content(image_prompt_parts)
        image_analysis_result = json.loads(image_response.text)

        # Log the spoken text
        print("Spoken Text:")
        print(spoken_text)

        # Log the image model response
        print("Image Model Response:")
        print(json.dumps(image_analysis_result, indent=2))

        response_text = image_analysis_result["Response"]
        text_tool = image_analysis_result["Text_Tool"]
        material_info = image_analysis_result.get("Material")  # Get item info if available

        # Select the appropriate function based on the tool
        if text_tool == "A":
            result = generate_nature_response(response_text, spoken_text)
        elif text_tool == "B":
            result = generate_recycling_response(response_text, spoken_text, material_info, image_parts[0])
        elif text_tool == "C":
            result = generate_greenwashing_response(response_text, spoken_text, material_info, image_parts[0])
        elif text_tool == "D":
            result = generate_composting_response(response_text, spoken_text)
        elif text_tool == "E":
            result = generate_food_response(response_text, spoken_text)
        elif text_tool == "F":
            result = generate_eco_response(response_text, spoken_text)
        else:
            raise ValueError("Invalid Text_Tool")

        # Log the text model response
        print("Text Model Response:")
        print(json.dumps(result, indent=2))
        result["text_tool"] = text_tool
        result["image_response"] = response_text
        result["material_info"] = material_info


        # Check if keyword is not included in the result
        if "keyword" not in result:
            result["keyword"] = []
        #it is impossible for the other three things to not be present, they are requisite

        return result

    except Exception as e:
        print(f"Error: {e}")
        return {'error': str(e)}
