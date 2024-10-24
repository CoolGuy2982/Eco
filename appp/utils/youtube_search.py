# youtube_search.py
# We use this to search youtube based on the inputted stuff
from googleapiclient.discovery import build

def create_youtube_service(credentials):
    return build('youtube', 'v3', credentials=credentials)

def search_youtube_video(credentials, query):
    youtube = create_youtube_service(credentials)
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
