from flask import Blueprint, render_template, request, jsonify, current_app, session
import threading
from .utils.image_analysis import analyze_image
from .utils.google_drive import upload_to_drive
import base64
import requests  # Standard requests module
from bs4 import BeautifulSoup
import urllib.parse
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests  # Renamed to avoid conflict
import os
import google.generativeai as genai
import time

# Create a Blueprint instance for the main app
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
    spoken_text = data.get('text')  # Ensure key matches 'text'
    
    # Log received data
    print("Received spoken text:", spoken_text)
    print("Received image data (truncated):", base64_image[:50], "...")

    result = analyze_image(base64_image, spoken_text)
    return jsonify(result)

@main.route('/upload', methods=['POST'])
def upload():
    data = request.get_json()
    base64_image = data.get('image')
    img_data = base64.b64decode(base64_image)
    upload_task = threading.Thread(target=upload_to_drive, args=("image.jpg", img_data))
    upload_task.start()
    return jsonify({'status': 'upload_started'})

@main.route('/scrape_address', methods=['GET'])
def scrape_address():
    what = request.args.get('what', '')
    latitude = request.args.get('latitude', '')
    longitude = request.args.get('longitude', '')
    keyword = urllib.parse.quote_plus(what)  # Encode the keyword properly
    url = f"https://search.earth911.com/?what={keyword}&latitude={latitude}&longitude={longitude}&max_distance=25"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    print(url)
    # Extract address parts using BeautifulSoup
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

    encoded_keyword = urllib.parse.quote_plus(keyword)  # Encode the keyword properly
    url = f"https://earthhero.com/search?q={encoded_keyword}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    products = []
    # Fetching top three products
    product_items = soup.select('.boost-pfs-filter-product-item')[:3]
    for item in product_items:
        image = item.select_one('.boost-pfs-filter-product-item-main-image.Image--lazyLoad')
        image_url = image.get('data-src', '') if image else 'No image found'
        
        title_tag = item.select_one('.boost-pfs-filter-product-item-title')
        title = title_tag.text.strip() if title_tag else 'No title found'
        
        # Select the price from the regular price class
        price_tag = item.select_one('.boost-pfs-filter-product-item-regular-price')

        # If not found, select the price from the sale price class
        if not price_tag:
            price_tag = item.select_one('.boost-pfs-filter-product-item-sale-price')

        # If still not found, set price to 'No price found'
        price = price_tag.text.strip() if price_tag else 'No price found'
        
        link = title_tag.get('href', '') if title_tag else 'No link found'

        products.append({
            'image_url': image_url,
            'title': title,
            'price': price,
            'link': f"https://earthhero.com{link}"  # Assuming relative URLs
        })

    # Log the image URLs for debugging
    print("Image URLs:", [product['image_url'] for product in products])

    return jsonify(products)

@main.route('/past-responses', methods=['GET'])
def past_responses_page():
    return render_template('past_responses.html')

system_prompt = """
Context:
You are a highly advanced AI model designed to analyze video content and provide eco-friendly advice tailored to the content of each video. Your analysis is based on a vast corpus of data related to environmental sustainability, recycling practices, product lifecycle assessment, ethical consumerism, and health implications of products and practices.

Video Input:
Assume you have access to video data streams or uploaded video files. These videos may range from consumer product reviews, recycling processes, environmental documentaries, or everyday activities that require ecological assessment.

Tasks:

Video Content Identification:

Automatically identify key visual elements in the video, such as products, natural scenes, activities, or text.
Determine the context of the video—whether it’s commercial, educational, advisory, or documentary.
Specific Analysis Based on Content Type:

For product reviews: Provide insights on the product's environmental impact, suggest eco-friendly alternatives, and highlight any greenwashing tactics used in the product's marketing.
For recycling processes: Offer detailed advice on how to properly recycle materials shown in the video, including local recycling guidelines and tips for reducing waste.
For environmental documentaries: Summarize key points, provide factual corrections if needed, and suggest ways viewers can contribute positively to the issues discussed.
For daily activities: Give practical eco-friendly advice tailored to the activities shown, such as energy-saving tips, sustainable living practices, or eco-conscious purchasing decisions.
Ethical and Health Considerations:

When products are shown, analyze their potential health impacts and ethical considerations of their production and use.
Suggest healthier, more ethical alternatives if available.
Comprehensive Eco-Friendly Advice:

Based on the video content, compile a comprehensive guide on improving environmental impact, considering global sustainability standards and local context.
Offer actionable steps that the viewer can take to mitigate negative environmental impacts in their daily lives or business operations.
Interactive Elements:

Provide questions or prompts to engage viewers, encouraging them to think critically about their environmental impact.
Offer links to resources for further learning or to support environmental initiatives related to the video content.
Example Use Cases:

A video showing various packaged foods: Analyze the packaging materials for recyclability, suggest eco-friendly packaging alternatives, and discuss the carbon footprint of typical production methods.
A clip from a store walkthrough highlighting different brands: Discuss each brand’s environmental and ethical track record, pointing out instances of greenwashing and providing advice on choosing genuinely sustainable options.
Output:
Your output should be a detailed, well-organized response suitable for the given video context, packed with specific, actionable advice, links to resources, and any necessary disclaimers about the information provided.
Also make the response very friendly because you want them to come back and give you more video next time and keep using the app, so make sure that they enjoy readiny your response and feel like you are their friend. Make responses really brief as possible too so they can read and get most out of it on the go.
"""

@main.route('/video', methods=['POST'])
def process_video():
    video = request.files['video']
    text = request.form.get('text', '')  # Optional additional user context

    # Combining the system prompt with any user-provided context
    full_prompt = system_prompt + "\nUser Context: " + text
    
    if video and video.content_length < 30 * 1024 * 1024:  # Check if file size < 30 MB
        video_path = f"./tmp/{video.filename}"
        video.save(video_path)  # Save video to a temporary directory

        try:
            # Upload the video using the File API
            video_file = genai.upload_file(path=video_path)

            # Check the file state until it's either processed or fails
            while video_file.state.name == "PROCESSING":
                time.sleep(10)
                video_file = genai.get_file(video_file.name)

            if video_file.state.name == "FAILED":
                return jsonify({"error": "Video processing failed"}), 500

            # Make the LLM request
            model = genai.GenerativeModel(model_name="gemini-1.5-flash")
            response = model.generate_content([video_file, full_prompt], request_options={"timeout": 600})
            print(response.text)
            return jsonify({"result": response.text})
        
        finally:
            # Clean up: delete the uploaded video file from the server
            if os.path.exists(video_path):
                os.remove(video_path)

    else:
        return jsonify({"error": "No video or file too large"}), 400
