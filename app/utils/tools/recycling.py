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

SCOPES = [
    'https://www.googleapis.com/auth/cloud-platform',
    'https://www.googleapis.com/auth/generative-language.retriever',
    'https://www.googleapis.com/auth/youtube.force-ssl'
]

#creds, project = google.auth.default(scopes=SCOPES)
SERVICE_ACCOUNT_FILE = 'service_account_key.json'
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

retriever_service_client = glm.RetrieverServiceClient(credentials=creds)
generative_service_client = glm.GenerativeServiceClient(credentials=creds)

def create_youtube_service():
    youtube = build('youtube', 'v3', credentials=creds)
    return youtube

def search_youtube_video(query):
    youtube = create_youtube_service()
    search_response = youtube.search().list(
        q=query,
        part='id,snippet',
        maxResults=1
    ).execute()

    if 'items' in search_response and len(search_response['items']) > 0:
        video_id = search_response['items'][0]['id']['videoId']
        return video_id
    else:
        return None

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
    if answerable_probability <= 0.7:
        model = genai.GenerativeModel(model_name='gemini-1.5-flash',
                                       generation_config={
                                            "temperature": 0.3,
                                            "top_p": 1,
                                            "top_k": 40,
                                            "max_output_tokens": 2048,
                                            "response_mime_type": "application/json"
                                        },
                                        safety_settings=[{"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}])
        response = model.generate_content(user_query, base64_image)
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

    Ensure the response is concise, relevant, and helpful, avoiding any irrelevant or obvious information. The response should feel conversational and caring:
    
    Don't respond in bullet points, respond in the same syntax as if you are texting someone. Appropriately give your response so it isn't intimidating to comprehend.
    Limit response to 80 words max.

    Give it in this JSON format:
    {{
    "Response": "[Your response here]",
    "Video_Suggestion": "<When appropriate, add a search query to search for a DIY project on YouTube using this item>"
    "Keyword": "<state what item it is about from the image description in a general sense ex. keyboard, water bottle, phone. (Note: not concepts such as greenwashing or sustainability, not just the name of the material like plastic or metal, not too specific like Plastic Phone Case, just phone case, water bottle, phone, backpack, etc. is good)>"
    }}
    """

    corpus_resource_name = "corpora/my-corpus-94qlvnd3wanj"

    try:
        # Handle the user query with RAG
        rag_response = handle_user_query(corpus_resource_name, text_prompt, base64_image)

        if rag_response is None:
            return {'error': "Query response structure is unexpected."}

        try:
            # Attempt to parse the response
            text_analysis_result = json.loads(rag_response)
            response = text_analysis_result.get("Response", "No response generated.")
            keyword = text_analysis_result.get("Keyword", "Unknown")
            video_suggestion = text_analysis_result.get("Video_Suggestion")
        except json.JSONDecodeError:
            # If JSON parsing fails, use Gemini 1.5 Flash model
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
            # Parse the fallback model's JSON response
            fallback_result = json.loads(alt_response.text)
            response = fallback_result.get("Response", "No response generated.")
            keyword = fallback_result.get("Keyword", "Unknown")
            video_suggestion = fallback_result.get("Video_Suggestion")

        result = {'result': response, 'keyword': keyword}

        # Use YouTube API to get a video ID, regardless of the response source
        if video_suggestion:
            video_id = search_youtube_video(video_suggestion)
            if video_id:
                result['video_suggestion'] = video_id

        return result

    except Exception as e:
        return {'error': str(e)}

