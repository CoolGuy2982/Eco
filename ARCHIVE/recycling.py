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

# this file houses the function to generate a recycling related response and give those insights from the image if the image analysis deems it to most valuable for recycling insights
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

def search_youtube_video(query, keyword=None):
    youtube = create_youtube_service()

    # Preset video IDs for specific keywords
    preset_videos = {
        "bottle": "JvhS58YoA6A",
        "box": "JhfP7l1uH4Y",
        "paper": "EeoUcfkG9go",
        "can": "L0A8HY9Gdgs",
        "wrapper": "8hDXZ8cY5oU",
        "container": "G2CprwP5AK4",
        "bag": "P_TmV66e6rk",
        "cup": "T2aJ4DXgV4M",
        "jar": "dF9TNo37jYw",
        "cardboard": "F0TJSjSk5DU"
    }

    try:
        # Perform YouTube search
        search_response = youtube.search().list(
            q=query,
            part='id,snippet',
            maxResults=1
        ).execute()

        if 'items' in search_response and search_response['items']:
            item = search_response['items'][0]
            if 'id' in item and 'videoId' in item['id']:
                video_id = item['id']['videoId']

                # Fetch video details for dimensions
                video_details = youtube.videos().list(
                    part='contentDetails,player',
                    id=video_id
                ).execute()

                if 'items' in video_details and video_details['items']:
                    content_details = video_details['items'][0].get('contentDetails', {})
                    player_details = video_details['items'][0].get('player', {})

                    # Extract video dimensions if available (fallback to default 16:9)
                    video_height = player_details.get('embedHeight')
                    video_width = player_details.get('embedWidth')

                    if video_height and video_width:
                        aspect_ratio = round(float(video_width) / float(video_height), 2)
                    else:
                        aspect_ratio = 16 / 9  # Default fallback

                    return {
                        'video_id': video_id,
                        'aspect_ratio': aspect_ratio
                    }

        # Fallback to preset video if no valid result
        fallback_video_id = preset_videos.get(keyword.lower() if keyword else "", 'dQw4w9WgXcQ')
        return {
            'video_id': fallback_video_id,
            'aspect_ratio': 16 / 9  # Default fallback
        }

    except Exception as e:
        print(f"YouTube API call failed: {e}")
        return {
            'video_id': 'dQw4w9WgXcQ',
            'aspect_ratio': 16 / 9  # Default fallback
        }

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
        print("1.5 Flash Recycling response: ")
        print(response.text)
        return response.text

    try:
        answer_content = aqa_response.answer.content.parts[0].text
    except AttributeError:
        print("Error: The expected field was not found in the AQA response.")
        return None

    return answer_content

def generate_recycling_response(response_text, spoken_text, material_info, base64_image):
    text_prompt = f"""
    You're an expert at Recycling and know everything about it at an extreme scientific level. 
    
    Feeling unsure about recycling certain items at home can be challenging, especially when you want to make environmentally responsible decisions. Based on the image you've sent and your local recycling regulations:

    Item Identification: Identify the item in the image, noting any specific materials it's made from, such as plastics, metals, electronics, or composites. Describe any labels or symbols that indicate potential recyclability.

    Local Recycling Guidelines:

    Check Local Rules: Cross-reference the item with recycling rules. Do most communities specifically accept this type of material? Are there special disposal instructions?
    Drop-off Points: If the item isn't curbside-recyclable, provide information about nearby recycling centers or drop-off locations that accept it.
    Material Specifics:

    Material Composition: Offer detailed insights about the materials used in the product, such as the type of plastic (e.g., PET, HDPE) and their general recyclability.
    Complex Components: Discuss components like batteries or electronics that might need special handling.
    Recycling Process:

    Explain the Recycling Process: Describe how the recycling process works for this type of material. What happens to the item once it's recycled? What products might it become in its next life?
    Environmental Impact: Share insights on the environmental benefits of recycling this material versus sending it to a landfill.
    Expert Tips:

    Reduce, Reuse, Recycle: Provide expert tips on reducing waste or reusing materials before opting to recycle.
    Innovations in Recycling: Briefly mention any new technologies or methods in recycling that could apply to this item, showcasing interesting developments in the field.
    Encouragement and Support:

    Motivational Note: Reassure the user that asking questions and seeking clarity is key to effective recycling and environmental stewardship.
    Continual Learning: Suggest resources for learning more about recycling and staying updated with local waste management practices.
    Conclude the response with friendly, supportive advice, making the information engaging and accessible. Ensure the tone is encouraging, helping the user feel confident about their recycling choices and more knowledgeable about how to contribute positively to the planet's health.

    Here is the spoken text provided by the user for additional context:
    {spoken_text}
    
    Here is the description you should use for your analysis:
    {response_text} 
    Material Info: {material_info}

    Ensure the response is concise, relevant, and helpful, avoiding any irrelevant or obious information. The response should feel conversational and caring:
    
    Don't respond in bullet points, respond in the same syntax as if you are texting someone. Appropriately give your response so it isn't intimidating to comprehend.
    Limit response to 80 words max.

    ALWAYS give it in this JSON format NO MATTER WHAT:
    {{
    "Response": "[Your response here]",
    "Video_Suggestion": "<When appropriate, add a search query to search for a DIY project on YouTube using this item>"
    "Keyword": "<state what item it is about from the image description in a general sense ex. keyboard, water bottle, phone. (Note: not concepts such as greenwashing or sustainability, not just the name of the material like plastic or metal, not too specific like Plastic Phone Case, just phone case, water bottle, phone, backpack, etc. is good)>"
    }}
    """

    corpus_resource_name = "corpora/my-corpus-dz1zhwuxelzw"

    # Initialize the result dictionary at the beginning
    result = {
        'result': None,
        'keyword': None,
        'video_suggestion': None,
        'aspect_ratio': None
    }

    try:
        rag_response = handle_user_query(corpus_resource_name, text_prompt, base64_image)
        print(rag_response)

        if rag_response is None:
            return {'error': "Query response structure is unexpected."}

        try:
            text_analysis_result = json.loads(rag_response)
            response = text_analysis_result.get("Response", "No response generated.")
            keyword = text_analysis_result.get("Keyword", "Unknown")
            video_suggestion = text_analysis_result.get("Video_Suggestion")

            # Populate the result dictionary
            result['result'] = response
            result['keyword'] = keyword
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
            print("Alt response: ")
            print(alt_response)

            fallback_result = alt_response.text

            # Parse the fallback response
            text_analysis_result = json.loads(fallback_result)
            response = text_analysis_result.get("Response", "No response generated.")
            keyword = text_analysis_result.get("Keyword", "Unknown")
            video_suggestion = text_analysis_result.get("Video_Suggestion")

            # Populate the result dictionary
            result['result'] = response
            result['keyword'] = keyword

        print("The video suggestion query: ", video_suggestion)

        if video_suggestion:
            try:
                # Call the YouTube search function and log the returned data
                video_data = search_youtube_video(video_suggestion)
                print("Video data returned:", video_data)

                # Directly extract video_id and aspect_ratio without extra checks
                video_id = video_data.get('video_id', None)
                aspect_ratio = video_data.get('aspect_ratio', 16 / 9)

                if video_id:
                    # Populate the result dictionary
                    result['video_suggestion'] = video_id
                    result['aspect_ratio'] = round(aspect_ratio, 2)
                    print(f"Using video ID: {video_id} with aspect ratio: {aspect_ratio}")
                else:
                    print("No valid video ID found. Skipping video suggestion.")
            except Exception as e:
                # Catch any exceptions during the try block
                print(f"Error while processing video suggestion: {e}")
                result['video_suggestion'] = 'dQw4w9WgXcQ'
                result['aspect_ratio'] = 16 / 9  # Default fallback



        print("Video suggestion:", result.get('video_suggestion', 'None'))
        print("Aspect ratio:", result.get('aspect_ratio', 'Unknown'))
        return result

    except Exception as e:
        return {'error': str(e)}