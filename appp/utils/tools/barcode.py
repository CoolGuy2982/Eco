import google.generativeai as genai
import os
import base64
from PIL import Image
from io import BytesIO
from pyzbar.pyzbar import decode
import requests

# Configure Google generative AI API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# Function to decode barcode from base64 image
def decode_barcode(base64_image):
    image_data = base64.b64decode(base64_image)
    image = Image.open(BytesIO(image_data))
    decoded_objects = decode(image)
    if decoded_objects:
        return decoded_objects[0].data.decode('utf-8')
    return None

# Function to get product info from UPC Database API using your API key
def get_product_info(barcode):
    API_URL = "https://api.upcdatabase.org/product/"
    API_KEY = "351AA03390FEA86FBCD939F3E03CBC3"  # Your UPC Database API key
    params = {
        'apikey': API_KEY,
        'upc': barcode
    }
    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        return response.json()
    return None

# Function to generate response with generative AI
def generate_barcode_response(response_text, spoken_text, base64_image):
    barcode = decode_barcode(base64_image)
    product_info = get_product_info(barcode) if barcode else {}

    # Prepare the prompt with product info if available
    product_details = f"Product Name: {product_info.get('title', 'Unknown')}, Brand: {product_info.get('brand', 'Unknown')}" if product_info else "Barcode could not be decoded or product not found."

    text_prompt = f"""
    Echo back and analyze based on the following information from a barcode (environemntal, health, anything helpful):
    Spoken text: {spoken_text}
    Image text description: {response_text}
    Product details from barcode: {product_details}
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
