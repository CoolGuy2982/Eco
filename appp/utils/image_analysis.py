import os
import base64
import google.generativeai as genai
import json
from .tools.nature import generate_nature_response
from .tools.food import generate_food_response
#adjust this so that text prompt is better in UI and also I can say, find some good vegan meal options restaurants near me and itll pick food and find them for me
from .tools.recycling import generate_recycling_response
from .tools.greenwashing import generate_greenwashing_response
from .tools.composting import generate_composting_response
from .tools.general_eco import generate_eco_response
from .tools.recipe import generate_recipe_response
from .tools.plants import generate_plant_response
from .tools.biodiversity import generate_biodiversity_response
from .tools.microscope import generate_microscope_response
from .tools.barcode import generate_barcode_response

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
Analyze the image in detail and provide a comprehensive description without mentioning people or humans. If there is a red box in the image, the user emphasizes what's in that red box. Follow these steps:

1. Main Purpose Identification: Determine the main purpose of the image by analyzing its contents and considering the user query: {spoken_text}. Use these observations to select the most fitting tool:
    
    - Nature (Tool A): Choose this if the image prominently features nature and natural environments such as forests, rivers, mountains, wildlife, or nature in general. Look for elements that emphasize ecological dynamics.
    - Recycling (Tool B): Choose this if the image features any item/product in a home or outdoor setting or generally looks like trash. This could be any type of item/product.
    - Greenwashing (Tool C): Opt for this if the image shows products in a commercial setting, like a store, being advertised with environmental claims. Look for labels like "eco-friendly," "sustainable," "green," "ethical," "organic," or "natural" on packaging, particularly in contexts that might suggest exaggerated or misleading claims.
    - Composting (Tool D): Use this if the image includes biodegradable materials suitable for composting. This might include food scraps, yard debris like leaves and grass, or other organic waste clearly intended to decompose in a compost setting.
    - Food (Tool E): Choose this tool if the image displays food storage or preparation areas such as kitchens, pantries, or refrigerators, featuring ingredients either being used for cooking or stored for future use, or food items.
    - Recipe (Tool F): Use this tool if the image features multiple ingredients that can be used to create a dish. This typically applies to kitchens, fridges, pantries, or other culinary settings.
    - Plant (Tool G): Select this if the image focuses on individual plants or garden settings.
    - Biodiversity (Tool H): Use this tool if the image showcases diverse ecosystems or multiple species.
    - Microscope (Tool I): Choose this tool for images with microscopic details.
    - Barcode (Tool J): Use this tool for images where barcodes are prominently displayed and may need analysis.
    - Eco Response (Tool K): Choose this if the image addresses a specific environmental issue or query.

Hints: Generally, the item in question, if there is one, will be in the center of the frame.

ANY PICTURE WITH AN ITEM (not food, compost, or nature things) WILL ALWAYS GO TO TOOLS B or C. NEVER ANYTHING ELSE. BE very deliberate with your tool choice. It needs to be perfect.
IF IT IS AN ITEM IN QUESTION IN A HOME OR A SPECIFIC PRODUCT IN FOCUS OUTDOORS ENVIRONMENT, IT WILL ALWAYS GO TO RECYCLING (Tool B)
IF IT IS AN ITEM IN A STORE OR COMMERCIAL PLACE, IT WILL ALWAYS GO TO GREENWASHING (Tool C) 

2. Detailed Description: Based on the selected tool, provide a detailed description focusing on the following aspects:
   - Nature (Tool A):
       - Identification: Identify the primary object or scene, including specific species of plants and animals.
       - Condition: Note any visible features such as health, growth stage, or signs of disease.
       - Composition: Describe key characteristics of the species, including size, color, and distinctive features.
       - Contextual Clues: Consider surrounding elements that provide ecological context, such as other species or environmental conditions.
       - Special Characteristics: Highlight unique features relevant to biodiversity insights, like habitat details or ecological interactions.
       - Conversational Directive: "Nature Specialist, please review this scene. We're focusing on the variety of plants and possible wildlife interactions."

   - Recycling (Tool B):
       - Identification: Identify the primary item, including specific types like type 3 plastic or aluminum Coca-Cola can.
       - Condition: Note any visible features such as contamination or damage.
       - Text Details: Note any text on the item related to the material of the packaging.
       - Composition: Describe materials or components of the item, including recyclability information.
       - Contextual Clues: Consider surrounding items that provide context, such as packaging or location.
       - Special Characteristics: Highlight any greenwashing aspects or other sustainability insights, including label information.
       - Conversational Directive: "Recycling Specialist, there's a potential recyclable item here. Could you verify its material and recyclability?"

   - Greenwashing (Tool C):
       - Identification: Identify the primary item, including specific types like type 3 plastic or aluminum Coca-Cola can.
       - Condition: Note any visible features such as contamination or damage.
       - Composition: Describe materials or components of the item, including recyclability information.
       - Contextual Clues: Consider surrounding items that provide context, such as packaging or location.
       - Special Characteristics: Highlight any greenwashing aspects or other sustainability insights, including label information.
       - Text Details: Transcribe all visible text on the packaging/product.
       - Conversational Directive: "Greenwashing Specialist, can you check these 'eco-friendly' claims on this product? We need your expert assessment."

   - Composting (Tool D):
       - Identification: Identify the primary compostable item, such as vegetable scraps or garden waste.
       - Condition: Note any visible features such as freshness or decomposition.
       - Composition: Describe the organic material and its compostability.
       - Contextual Clues: Consider surrounding elements that provide context, such as other compostable items or compost bins.
       - Special Characteristics: Highlight any signs of successful or unsuccessful composting.
       - Conversational Directive: "Composting Specialist, please evaluate this organic waste for composting suitability."

   - Food (Tool E):
       - Identification: Identify the ingredients shown in a fridge, pantry, or the frame.
       - Condition: Note any visible features such as freshness or spoilage.
       - Quantity: List the general quantities of the ingredients.
       - Composition: List all the ingredients and their quantities if visible.
       - Contextual Clues: Consider surrounding items that provide culinary context, such as other ingredients or kitchen tools.
       - Conversational Directive: "Food Specialist, could you assess the condition and potential use of these ingredients?"

   - Recipe (Tool F):
       - Identification: Identify the primary ingredients visible in the setting.
       - Condition: Note the freshness and usability of these ingredients for cooking.
       - Composition: Describe the potential combinations of ingredients for a dish.
       - Contextual Clues: Include any visible recipe books or cooking tools that suggest specific dishes.
       - Special Characteristics: Highlight any unique or specialty ingredients.
       - Conversational Directive: "Recipe Specialist, we have a variety of ingredients here. What dish could these be used for?"

   - Plant (Tool G):
       - Identification: Identify the plant species or type shown in the image.
       - Condition: Assess the health, growth stage, and any visible characteristics of the plant.
       - Composition: Describe the plant's size, leaf shape, color, and any flowers or fruits.
       - Contextual Clues: Consider the surrounding environment, such as garden elements or indoor settings.
       - Special Characteristics: Highlight unique features, such as rare species or specific cultivation details.
       - Conversational Directive: "Plant Specialist, can you identify and describe the plant shown in the image?"

   - Biodiversity (Tool H):
       - Identification: Identify the range of species present in the image.
       - Condition: Note the health and state of the different species.
       - Composition: Describe the biodiversity, including species variety and interactions.
       - Contextual Clues: Consider the habitat and ecological context, like water sources or vegetation.
       - Special Characteristics: Highlight any notable ecological interactions or rare species.
       - Conversational Directive: "Biodiversity Specialist, please analyze the diversity of species in this scene."

   - Microscope (Tool I):
       - Identification: Identify the microscopic elements or organisms visible.
       - Condition: Note any distinguishing features, including health or structural details.
       - Composition: Describe the microscopic details, such as cell structure or microorganism characteristics.
       - Contextual Clues: Include any related equipment or context that might provide additional insights.
       - Special Characteristics: Highlight any unique findings or anomalies observed.
       - Conversational Directive: "Microscope Specialist, can you detail the microscopic features visible here?"

   - Barcode (Tool J):
       - Identification: Identify the barcodes present in the image.
       - Condition: Note any issues with readability or damage.
       - Composition: Describe the context in which the barcode is found, such as on packaging or labels.
       - Contextual Clues: Consider any associated products or information linked to the barcode.
       - Special Characteristics: Highlight any unique identifiers or codes.
       - Conversational Directive: "Barcode Specialist, can you provide information on the barcodes present in this image?"

   - Eco Response (Tool K):
       - Identification: Identify the specific environmental issue or element in question.
       - Condition: Note any relevant features or states that pertain to the issue.
       - Composition: Describe the components or materials involved.
       - Contextual Clues: Consider surrounding elements that provide additional context.
       - Special Characteristics: Highlight any critical insights or notable aspects related to the environmental issue.
       - Conversational Directive: "Eco Response Specialist, what environmental issues can you identify in this image?"

Note: add anything worth mentioning in the conversational directive (who is making a response for the user) to make the response as useful, enjoyable, and beneficial for the user as possible.
MAKE SURE TO PROVIDE REASONING, THOUGHT PROCESS, CHAIN OF THOUGHT FOR WHY YOU CHOSE THE TOOL YOU CHOOSE. WHAT IN THE IMAGE/WHAT REASONING MADE YOU CHOOSE IT. Be very descriptive and cite evidence from the image. Think step by step and logically. Take a deep breath.
Take a deep breath and work on this problem step-by-step.

3. JSON Response: Format the response as follows (example):
{{
    "Response": "<detailed description>",
    "Text_Tool": "A",
    "Material": "if you selected tool B <add the material of the general item if applicable (e.g., Plastic)>"
    "COT": "<State your reasoning HERE>"
}}
            """,
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
            result = generate_nature_response(response_text, spoken_text, image_parts[0])
        elif text_tool == "B":
            result = generate_recycling_response(response_text, spoken_text, material_info, image_parts[0])
        elif text_tool == "C":
            result = generate_greenwashing_response(response_text, spoken_text, material_info, image_parts[0])
        elif text_tool == "D":
            result = generate_composting_response(response_text, spoken_text)
        elif text_tool == "E":
            result = generate_food_response(response_text, spoken_text, image_parts[0])
        elif text_tool == "F":
            result = generate_recipe_response(response_text, spoken_text,image_parts[0])
        elif text_tool == "G":
            result = generate_plant_response(response_text, spoken_text,image_parts[0])
        elif text_tool == "H":
            result = generate_biodiversity_response(response_text, spoken_text,image_parts[0])
        elif text_tool == "I":
            result = generate_microscope_response(response_text, spoken_text,image_parts[0])
        elif text_tool == "J":
            result = generate_barcode_response(response_text, spoken_text,image_parts[0])
        elif text_tool == "K":
            result = generate_eco_response(response_text, spoken_text,image_parts[0])
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
