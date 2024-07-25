import os
import base64
from PIL import Image
from io import BytesIO
from pyzbar.pyzbar import decode
import requests
import threading
import google.generativeai as genai

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
    # Fetches the image from the URL and converts it to a base64 encoded string
    response = requests.get(image_url)
    if response.status_code == 200:
        return base64.b64encode(response.content).decode('utf-8')  # Return base64 string
    else:
        return None

def get_image_from_open_food_facts(barcode, results):
    URL = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(URL)
    
    if response.status_code == 200:
        data = response.json()
        image_url = data.get('product', {}).get('image_front_url', None)
        if image_url:
            base64_image_data = get_image_data_from_url(image_url)
            results['open_food_facts'] = {
                'base64_image_data': base64_image_data,
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
    base64_image_data = image_info.get('base64_image_data', None)
    image_url = image_info.get('image_url', 'URL not available if not found.')
    
    print("Ok now we can generate")

    text_prompt = f"Analyze the product in the image. User Query: {spoken_text}. Also give environmental and health analysis based on the image."

    # Prepare image data for model
    if base64_image_data:
        image_data = base64.b64decode(base64_image_data)
        image_parts = [{"mime_type": "image/jpeg", "data": image_data}]

        # Sending image data with MIME type and text prompt to the model
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

        image_response = text_model.generate_content([image_parts[0], text_prompt])
        text_analysis_result = image_response.text

        return {
            'result': text_analysis_result,
            'barcode_image_url': image_url  # Return the image URL in the response
        }
    else:
        print("Image data not available.")
        return None

# Example usage:
# spoken_text = "Describe the nutritional content."
# base64_image = "your_base64_encoded_image_string_here"
# result = generate_barcode_response(spoken_text, base64_image)
# print(result)
