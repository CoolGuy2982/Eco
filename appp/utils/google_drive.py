import os
from google.auth import default
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/drive.file']

# folder ID of the Google Drive folder where files will be uploaded
DRIVE_FOLDER_ID = '14_AeV9n8Nt5pZNwuigD6aE_nwXoW8_aw' 

def get_credentials():
    """Get credentials either from the default environment or from a service account file."""
    try:
        #try to get default credentials (e.g., when running in a deployed environment like App Engine, Cloud Run, etc.)
        creds, project = default(scopes=SCOPES)
        return creds
    except Exception as e:
        # if default credentials don't work, try using a service account key file locally
        print("Using the local key")
        SERVICE_ACCOUNT_FILE = os.getenv('GCP_SERVICE_ACCOUNT_KEY_PATH')
        if not SERVICE_ACCOUNT_FILE:
            raise Exception("Service account file path is not set in environment variables.")
        
        creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        return creds

# Create a Google Drive service using the obtained credentials
drive_service = build('drive', 'v3', credentials=get_credentials())

def upload_to_drive(file_name, file_data):
    """Upload a file to Google Drive."""
    try:
        # Prepare metadata for the file (file name and folder to upload to)
        file_metadata = {
            'name': file_name,
            'parents': [DRIVE_FOLDER_ID]
        }

        # create a media upload object with file data and MIME type
        media = MediaIoBaseUpload(BytesIO(file_data), mimetype='image/jpeg')

        # make the API request to upload the file to GDrive
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        return file.get('id')
    except Exception as e:
        print(f"Error uploading file to Google Drive: {str(e)}")
        return None

