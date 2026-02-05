from flask import Blueprint, render_template, request, jsonify, current_app, session
import threading
from .utils.image_analysis import analyze_image
from .utils.google_drive import upload_to_drive
import base64
import requests 
from bs4 import BeautifulSoup
import urllib.parse
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests  # renamed to avoid conflict
import os
import google.generativeai as genai
import time
# routes.py is critical because it has all the endpoints and is how through flask framework the frontend and backend can interact
main = Blueprint('main', __name__)

CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')


@main.route('/login', methods=['POST'])
def login():
    token = request.json.get('idToken')
    try:
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), CLIENT_ID)
        user_email = idinfo['email']
        session['user_email'] = user_email
        return jsonify({'success': True})
    except ValueError:
        return jsonify({'success': False}), 401

@main.route('/')
def splash():
    return render_template('splash.html')

@main.route('/home')
def home():
    return render_template('home.html')

@main.route('/camera')
def camera():
    return render_template('camera.html')

@main.route('/browse')
def browse():
    return render_template('browse.html')

@main.route('/ecopoints')
def ecopoints():
    return render_template('ecopoints.html')

#############################################################
# Apps
#############################################################
@main.route('/generaleco')
def generaleco():
    return render_template('apps/generaleco.html')


@main.route('/generaleco/footprint')
def footprint():
    return render_template('apps/general_eco_apps/footprint.html')

@main.route('/generaleco/earth911')
def earth911():
    return render_template('apps/general_eco_apps/earth911.html')
##############################################################
@main.route('/nature')
def nature():
    return render_template('apps/naturewalk.html')

@main.route('/nature/inaturalist')
def inaturalist():
    return render_template('apps/nature_apps/inaturalist.html')

@main.route('/nature/soundmap')
def soundmap():
    return render_template('apps/nature_apps/sound_map.html')

@main.route('/nature/recorder')
def naturesoundrecorder():
    return render_template('apps/nature_apps/naturesoundrecorder.html')

################################################################
@main.route('/recycling')
def recycling():
    return render_template('apps/recycling.html')

@main.route('/recycling/earth911search')
def recyclingsearchapps():
    return render_template('apps/recycling_apps/earth911search.html')

#################################################################
@main.route('/greenwashing')
def greenwashing():
    return render_template('apps/greenwashing.html')

@main.route('/greenwashing/index')
def greenwashingindex():
    return render_template('apps/greenwashing_apps/ecolabel.html')

#################################################################
@main.route('/composting')
def composting():
    return render_template('apps/composting.html')
#################################################################

@main.route('/food')
def food():
    return render_template('apps/food.html')

@main.route('/food/seasonal')
def foodseasonal():
    return render_template('apps/food_apps/seasonal.html')

#################################################################

@main.route('/suggestions')
def suggestions():
    return render_template('apps/suggestions.html')

@main.route('/profile')
def profile():
    return render_template('profile.html')

@main.route('/analysis')
def analysis():
    google_maps_api_key = current_app.config.get('GOOGLE_MAPS_API_KEY')
    if not google_maps_api_key:
        raise ValueError("Google Maps API key not found in the configuration")
    return render_template('analysis.html', google_maps_api_key=google_maps_api_key)

@main.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    base64_image = data.get('image')
    spoken_text = data.get('text')  #make sure key matches 'text'
    
    #log received data
    print("Received spoken text:", spoken_text)
    print("Received image data (truncated):", base64_image[:50], "...")

    result = analyze_image(base64_image, spoken_text)
    return jsonify(result)

@main.route('/scrape_address', methods=['GET'])
def scrape_address():
    what = request.args.get('what', '')
    latitude = request.args.get('latitude', '')
    longitude = request.args.get('longitude', '')
    keyword = urllib.parse.quote_plus(what) 
    url = f"https://search.earth911.com/?what={keyword}&latitude={latitude}&longitude={longitude}&max_distance=25"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    print(url)
    # extract address parts using BeautifulSoup
    address1 = soup.find(class_='address1').text if soup.find(class_='address1') else 'Not found'
    address3 = soup.find(class_='address3').text if soup.find(class_='address3') else 'Not found'

    # Combine the parts into a single address string
    full_address = f"{address1}, {address3}"
    return jsonify({'address': full_address})

@main.route('/scrape_products', methods=['GET'])
def scrape_products():
    keyword = request.args.get('keyword', '')
    if not keyword:
        return jsonify({'error': 'No keyword provided'}), 400

    # scraping logic for Ecoternatives
    ecoternatives_url = f"https://ecoternatives.co/search?q={keyword}"
    eco_response = requests.get(ecoternatives_url)
    eco_soup = BeautifulSoup(eco_response.text, 'html.parser')

    eco_products = []
    eco_product_items = eco_soup.select('.card-wrapper .card.card--standard')  # More specific selector

    for item in eco_product_items:
        # Skip blog posts, articles, or pages by checking for specific labels
        blog_label = item.select_one('.badge')
        if blog_label and 'Blog' in blog_label.text:
            continue

        # Extract image URL
        image_tag = item.select_one('.card__media img')
        image_url = image_tag.get('src', '') if image_tag else 'No image found'

        # Extract product title and link
        title_tag = item.select_one('.card__heading a.full-unstyled-link')
        title = title_tag.text.strip() if title_tag else 'No title found'
        link = title_tag.get('href', '') if title_tag else 'No link found'
        full_link = f"https://ecoternatives.co{link}"

        # Extract price
        price_tag = item.select_one('.price-item--regular')
        price = price_tag.text.strip() if price_tag else 'No price found'

        eco_products.append({
            'image_url': image_url,
            'title': title,
            'price': price,
            'link': full_link
        })


    # Step 2 - Scrape the next 6 products from earthhero.com
    encoded_keyword = urllib.parse.quote_plus(keyword)
    earthhero_url = f"https://earthhero.com/search?q={encoded_keyword}"
    earthhero_response = requests.get(earthhero_url)
    earthhero_soup = BeautifulSoup(earthhero_response.text, 'html.parser')

    earthhero_products = []
    earthhero_product_items = earthhero_soup.select('.boost-pfs-filter-product-item')[:6]

    for item in earthhero_product_items:
        # Extract image URL
        image = item.select_one('.boost-pfs-filter-product-item-main-image.Image--lazyLoad')
        image_url = image.get('data-src', '') if image else 'No image found'

        # Extract product title and link
        title_tag = item.select_one('.boost-pfs-filter-product-item-title')
        title = title_tag.text.strip() if title_tag else 'No title found'
        link = title_tag.get('href', '') if title_tag else 'No link found'
        full_link = f"https://earthhero.com{link}"

        # Extract price
        price_tag = item.select_one('.boost-pfs-filter-product-item-regular-price')
        if not price_tag:
            price_tag = item.select_one('.boost-pfs-filter-product-item-sale-price')
        price = price_tag.text.strip() if price_tag else 'No price found'

        earthhero_products.append({
            'image_url': image_url,
            'title': title,
            'price': price,
            'link': full_link
        })

    # Step 3: Combine the products from both sources
    combined_products = eco_products + earthhero_products

    # Log the image URLs for debugging
    print("Image URLs (Ecoternatives):", [product['image_url'] for product in eco_products])
    print("Image URLs (EarthHero):", [product['image_url'] for product in earthhero_products])

    return jsonify(combined_products)

