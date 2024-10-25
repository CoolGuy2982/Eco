import os
from google.auth import default
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO
from google.oauth2 import service_account
from google.oauth2.service_account import Credentials

# folder ID of the Google Drive folder where files will be uploaded
DRIVE_FOLDER_ID = '14_AeV9n8Nt5pZNwuigD6aE_nwXoW8_aw' 

# Set your required scopes here
SCOPES = [
    'https://www.googleapis.com/auth/cloud-platform',
    'https://www.googleapis.com/auth/generative-language',
    'https://www.googleapis.com/auth/drive.file'
]

def get_credentials():
    try:
        # Attempt to use default credentials (works in Google Cloud)
        creds, project = default(scopes=SCOPES)
        print("Using default credentials.")
        return creds
    except Exception as e:
        print(f"Default credentials failed: {e}")

        # Fallback to service account credentials
        SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
        if not SERVICE_ACCOUNT_FILE:
            raise Exception("The GOOGLE_APPLICATION_CREDENTIALS environment variable is not set or points to an invalid file.")

        print("Using service account credentials from file.")
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        return creds

# Test credentials
creds = get_credentials()
print(f"Using credentials: {creds}")

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

