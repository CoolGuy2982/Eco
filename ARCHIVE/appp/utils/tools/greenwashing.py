import google.generativeai as genai
import google.oauth2.credentials
import os
import json
import google.ai.generativelanguage as glm
from google.auth import default
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import google.auth
from google.auth.transport.requests import Request

# this file houses the function to generate a greenwashing related response and give those insights from the image if the image analysis deems it to most valuable for greenwashing insights
# it sends the image again and user context for response generation. This allows for complex insights to be generated in a personalized way.

SCOPES = [
    'https://www.googleapis.com/auth/cloud-platform',
    'https://www.googleapis.com/auth/generative-language.retriever',
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/generative-language'
]


#creds, project = google.auth.default(scopes=SCOPES)

#SERVICE_ACCOUNT_FILE = 'service_account_key.json'
#creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

def get_credentials():
    try:
        # Attempt to use default credentials (works in Google Cloud)
        creds, project = default(scopes=SCOPES)
        # Check if the credentials are service account credentials
        if isinstance(creds, Credentials):
            print("Using service account credentials (loaded as default credentials).")
        else:
            print("Using default user credentials.")
        return creds
    except Exception as e:
        print(f"Default credentials failed: {e}")
        
        # Fallback to service account credentials
        SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'service_account_key.json')

        if not os.path.exists(SERVICE_ACCOUNT_FILE):
            raise Exception("The GOOGLE_APPLICATION_CREDENTIALS environment variable is not set or points to an invalid file.")

        print("Using service account credentials from file.")
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        return creds

retriever_service_client = glm.RetrieverServiceClient(credentials=get_credentials())
generative_service_client = glm.GenerativeServiceClient(credentials=get_credentials())


def create_youtube_service():
    youtube = build('youtube', 'v3',credentials= get_credentials())
    return youtube

def search_youtube_video(query, keyword):
    youtube = create_youtube_service()

    # preset video ids based on common keywords
    preset_videos = {
        "bottle": "JvhS58YoA6A",  # ddiy project with plastic bottles
        "box": "JhfP7l1uH4Y",     # diy crafts using cardboard boxes
        "paper": "EeoUcfkG9go",   # recycled paper projects
        "can": "L0A8HY9Gdgs",     # Aluminum can upcycling ideas
        "wrapper": "8hDXZ8cY5oU", # creative use of food wrappers
        "container": "G2CprwP5AK4", # DIY ideas using plastic containers
        "bag": "P_TmV66e6rk",     # diy projects with shopping bags
        "cup": "T2aJ4DXgV4M",     # crafts using disposable cups
        "jar": "dF9TNo37jYw",     # Reusing glass jars creatively
        "cardboard": "F0TJSjSk5DU" # projects with cardboard materials
    }

    try:
        search_response = youtube.search().list(
            q=query,
            part='id,snippet',
            maxResults=1
        ).execute()

        if 'items' in search_response and len(search_response['items']) > 0:
            item = search_response['items'][0]
            if 'id' in item and 'videoId' in item['id']:
                video_id = item['id']['videoId']
                return video_id
            else:
                print("The search result does not contain a videoId.")
                return None
        else:
            print("No items found in the search response.")
            return None

    except Exception as e:
        print(f"YouTube API call failed: {e}")
        
        # Use preset video ID based on the keyword
        fallback_video_id = preset_videos.get(keyword.lower(), 'dQw4w9WgXcQ')  # Default to Rickroll if no match
        print(f"Using fallback video for keyword '{keyword}': {fallback_video_id}")
        return fallback_video_id
    
def query_corpus(corpus_resource_name, user_query, results_count=5):
    query_request = glm.QueryCorpusRequest(
        name=corpus_resource_name,
        query=user_query,
        results_count=results_count
    )
    query_response = retriever_service_client.query_corpus(query_request)
    return query_response

def generate_answer(corpus_resource_name, user_query, answer_style="EXTRACTIVE"):
    content = glm.Content(parts=[glm.Part(text=user_query)])
    retriever_config = glm.SemanticRetrieverConfig(source=corpus_resource_name, query=content)
    generate_answer_request = glm.GenerateAnswerRequest(
        model="models/aqa",
        contents=[content],
        semantic_retriever=retriever_config,
        answer_style=answer_style,
        temperature=0.2
    )
    aqa_response = generative_service_client.generate_answer(generate_answer_request)
    return aqa_response

def handle_user_query(corpus_resource_name, user_query, base64_image, results_count=5):
    aqa_response = generate_answer(corpus_resource_name, user_query)
    print("HEre's the full AQA response: \n", aqa_response)
    answerable_probability = aqa_response.answerable_probability
    if answerable_probability <= 1.2:
        print("AQA Probability low")
        model = genai.GenerativeModel(model_name='gemini-1.5-flash',
                                       generation_config={
                                            "temperature": 0.3,
                                            "top_p": 1,
                                            "top_k": 40,
                                            "max_output_tokens": 2048,
                                            "response_mime_type": "application/json"
                                        },
                                        safety_settings=[{"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}])
        response = model.generate_content([user_query, base64_image])
        return response.text

    try:
        answer_content = aqa_response.answer.content.parts[0].text
    except AttributeError:
        print("Error: The expected field was not found in the AQA response.")
        return None

    return answer_content

def generate_greenwashing_response(response_text, spoken_text, material_info, base64_image):
    text_prompt = f"""
    Here is the spoken text provided by the user for additional context:
    {spoken_text}
    
    Here is the description you should use for your analysis:
    {response_text} 
    Material Info: {material_info}

        Analyze the image of the product provided, which is labeled as 'eco-friendly' or 'sustainable'. Based on the visible information, such as text, labels, and packaging material:

        Identify and List Claims:

        Detail the specific environmental claims made on the product packaging. Highlight any keywords or phrases like 'green', 'organic', 'recycled', or 'carbon neutral'.
        Identify any certifications or eco-labels present on the product, such as USDA Organic, Fair Trade, or Energy Star.
        Evaluate the Validity of These Claims:

        Assess the credibility of the certifications: Check if these certifications are appropriate and recognized within the industry.
        Material Analysis: Examine the materials listed or visible on the product. Determine if they align with sustainable practices, such as being truly recyclable or sourced sustainably.
        Compare and Provide Alternatives:

        Benchmark these claims against industry standards for similar eco-friendly products. Provide context on how genuine these claims might be compared to recognized sustainable products.
        If the claims appear suspect or lacking in transparency, suggest more reliable product alternatives available in the market that meet higher sustainability standards.
        Expert Insights and Advice:

        Offer insights into common greenwashing tactics that might be evident in the product’s marketing.
        Provide actionable steps the consumer can take to verify these claims further, such as specific aspects of the product's sustainability they might research or questions they could ask the retailer.
        Finish by providing these insights in a clear, concise manner to help the consumer make an informed decision about the product's sustainability claims, while also supporting them in identifying more transparent and ethically sound choices in the market.
    
    Don't respond in bullet points, respond like you are texting someone back. Appropriately space out your response so it isn't intimidating to read.
    Limit response to 80 words max.

    Give it in this JSON format:
    {{
    "Response": "[Your response here]",
    "Video_Suggestion": "<add a search query to search for a DIY project on YouTube using this item (Note: you don't have to add this if it doesn't make sense for the item)>"
    "Keyword": "<state what item it is about from the image description in a general sense ex. keyboard, water bottle, phone (Note: this is generalized items, not concepts such as greenwashing or sustainability)>"
    }}
    """

    corpus_resource_name = "corpora/my-corpus-dz1zhwuxelzw"

    try:
        rag_response = handle_user_query(corpus_resource_name, text_prompt, base64_image)

        if rag_response is None:
            return {'error': "Query response structure is unexpected."}

        try:
            text_analysis_result = json.loads(rag_response)
            response = text_analysis_result.get("Response", "No response generated.")
            keyword = text_analysis_result.get("Keyword", "Unknown")
            video_suggestion = text_analysis_result.get("Video_Suggestion")
        except json.JSONDecodeError:
            print("Houston we have a problem.")
            model = genai.GenerativeModel(model_name='gemini-1.5-flash',
                                           generation_config={
                                                "temperature": 0.3,
                                                "top_p": 1,
                                                "top_k": 40,
                                                "max_output_tokens": 2048,
                                                "response_mime_type": "application/json"
                                            },
                                            safety_settings=[{"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}])
            alt_response = model.generate_content([text_prompt, base64_image])

            print(alt_response)

            fallback_result = alt_response.text

            text_analysis_result = json.loads(fallback_result)
            response = text_analysis_result.get("Response", "No response generated.")
            keyword = text_analysis_result.get("Keyword", "Unknown")
            video_suggestion = text_analysis_result.get("Video_Suggestion")

        result = {'result': response, 'keyword': keyword}

        if video_suggestion:
            video_id = search_youtube_video(video_suggestion)
            if video_id:
                result['video_suggestion'] = video_id

        return result

    except Exception as e:
        return {'error': str(e)}