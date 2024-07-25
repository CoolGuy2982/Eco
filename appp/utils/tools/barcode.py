import google.generativeai as genai
import os
import base64
from PIL import Image
from io import BytesIO
from pyzbar.pyzbar import decode
import requests
import threading

# Configure Google Generative AI API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

def decode_barcode(base64_image):
    image_data = base64.b64decode(base64_image)
    image = Image.open(BytesIO(image_data))

    # Decode the barcode(s) in the image
    decoded_objects = decode(image)

    if decoded_objects:
        barcode_data = decoded_objects[0].data.decode('utf-8')
        return barcode_data
    else:
        return None

def get_image_data_from_url(image_url):
    # Fetches the image from the URL and converts it to raw binary data
    response = requests.get(image_url)
    if response.status_code == 200:
        return response.content  # Directly return raw image data
    else:
        return None

def get_image_from_open_food_facts(barcode, results):
    URL = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(URL)
    
    if response.status_code == 200:
        data = response.json()
        image_url = data.get('product', {}).get('image_front_url', None)
        if image_url:
            raw_image_data = get_image_data_from_url(image_url)
            results['open_food_facts'] = {
                'raw_image_data': raw_image_data,
                'image_url': image_url  # Store the URL in the results
            }
    else:
        results['open_food_facts'] = None

def generate_barcode_response(spoken_text, base64_image):
    barcode = decode_barcode(base64_image)
    print(f"Decoded Barcode: {barcode}")

    results = {}
    thread = threading.Thread(target=get_image_from_open_food_facts, args=(barcode, results))
    thread.start()
    thread.join()

    image_info = results.get('open_food_facts')
    raw_image_data = image_info.get('raw_image_data', None)
    image_url = image_info.get('image_url', 'URL not available if not found.')

    text_prompt = f"""
    Analyze the product in the image (environmental, health, anything helpful).
    User Query: {spoken_text}
    """

    # Sending raw image data and text prompt to the model
    text_model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={
            "temperature": 0.8,
            "top_p": 1,
            "top_k": 40,
            "max_output_tokens": 400,
        },
        safety_settings=[{"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}]
    )

    text_response = text_model.generate_content([raw_image_data, text_prompt])
    text_analysis_result = text_response.text

    return {
        'result': text_analysis_result,
        'image_url': image_url  # Return the image URL in the response
    }
