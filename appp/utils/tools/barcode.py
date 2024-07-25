import google.generativeai as genai
import os
import base64
from PIL import Image
from io import BytesIO
from google.cloud import vision
from google.oauth2 import service_account
import requests
from google.auth import default

# Set up Google Cloud Vision API
def get_credentials():
    # Use default credentials when deployed
    try:
        creds, project = default()
        return creds
    except Exception as e:
        # Fallback to service account key file locally
        SERVICE_ACCOUNT_FILE = os.getenv('GCP_SERVICE_ACCOUNT_KEY_PATH')
        creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
        return creds
    
vision_client = vision.ImageAnnotatorClient(credentials= get_credentials())

# Configure Google Generative AI API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

def decode_barcode(base64_image):
    image_data = base64.b64decode(base64_image)
    image = vision.Image(content=image_data)

    # Perform text detection
    response = vision_client.text_detection(image=image)
    texts = response.text_annotations

    if response.error.message:
        raise Exception(f'Error during text detection: {response.error.message}')

    # Extract barcode data
    for text in texts:
        if text.description.isdigit():  # Basic check, refine as needed
            return text.description
    return None

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

def generate_barcode_response(response_text, spoken_text, base64decoded_image, img_data):
    barcode = decode_barcode(img_data)
    product_info = get_product_info(barcode) if barcode else {}

    # Prepare the prompt with product info if available
    product_details = f"Product Name: {product_info.get('title', 'Unknown')}, Brand: {product_info.get('brand', 'Unknown')}" if product_info else "Barcode could not be decoded or product not found."

    text_prompt = f"""
    Echo back and analyze based on the following information from a barcode (environmental, health, anything helpful):
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

    text_response = text_model.generate_content([base64decoded_image, text_prompt])
    text_analysis_result = text_response.text

    return {
        'result': text_analysis_result
    }
