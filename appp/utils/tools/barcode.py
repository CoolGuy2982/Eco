import google.generativeai as genai
import os
import base64
from PIL import Image
from io import BytesIO
from pyzbar.pyzbar import decode
import requests
from bs4 import BeautifulSoup
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

def get_product_info_ean_search(barcode, results):
    URL = f"https://www.ean-search.org/?q={barcode}"
    response = requests.get(URL)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract product details
        product_name = soup.find('b').find_next('a').get_text(strip=True)
        issuing_country = soup.find('b', text="Issuing country:").next_sibling.strip()

        results['ean_search'] = {
            'product_name': product_name,
            'issuing_country': issuing_country
        }
    else:
        results['ean_search'] = None

def get_image_from_open_food_facts(barcode, results):
    URL = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(URL)
    
    if response.status_code == 200:
        data = response.json()
        image_url = data.get('product', {}).get('image_front_url', None)
        results['open_food_facts'] = {
            'image_url': image_url
        }
    else:
        results['open_food_facts'] = None

def generate_barcode_response(response_text, spoken_text, base64_image):
    barcode = decode_barcode(base64_image)
    print(f"Decoded Barcode: {barcode}")

    results = {}
    threads = []
    threads.append(threading.Thread(target=get_product_info_ean_search, args=(barcode, results)))
    threads.append(threading.Thread(target=get_image_from_open_food_facts, args=(barcode, results)))

    # Start all threads
    for thread in threads:
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    product_info = results.get('ean_search')
    image_info = results.get('open_food_facts')

    print(f"Product Info: {product_info}")
    print(f"Image Info: {image_info}")

    # Prepare the prompt with product info if available
    product_details = (
        f"Product Name: {product_info.get('product_name', 'Unknown')}, "
        f"Issuing Country: {product_info.get('issuing_country', 'Unknown')}"
    ) if product_info else "Barcode could not be decoded or product not found."

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

    text_response = text_model.generate_content([text_prompt])
    text_analysis_result = text_response.text

    return {
        'result': text_analysis_result,
        'product_details': product_details,
        'barcode_image_url': image_info.get('image_url', 'Image not available')
    }