import os
import base64
from PIL import Image
from io import BytesIO
from pyzbar.pyzbar import decode
import requests
import threading
import google.generativeai as genai

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
    response = requests.get(image_url)
    if response.status_code == 200:
        return base64.b64encode(response.content).decode('utf-8')  # return base64 string
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
                'image_url': image_url
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

    text_prompt = f"Analyze the product in the image. User Query: {spoken_text}. Also give environmental and health analysis based on the image. Keep response to 80 words max, make it sound natural and fun to read, not robotic and bullet points."

    # prepare image data for model
    if base64_image_data:
        image_data = base64.b64decode(base64_image_data)
        image_parts = [{"mime_type": "image/jpeg", "data": image_data}]

        try:
            # sending image data with mime type and text prompt to the model
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
                'barcode_image_url': image_url  # return the image URL in the response
            }
        except Exception as e:
            # handle any exceptions during content generation
            error_message = f"Hi there! The barcode stuff only works for food right now, so thank you for your patience and for using ecolens! <3"
            return {
                'result': error_message,
                'barcode_image_url': image_url  # return the image URL in the response
            }
    else:
        print("Image data not available.")
        return {
            'result': "Image data not available. Unable to generate content.",
            'barcode_image_url': image_url  # return the image URL in the response
        }
