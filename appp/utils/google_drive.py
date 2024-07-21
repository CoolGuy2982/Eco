import os
from google.auth import default
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO
from google.oauth2 import service_account
from google.auth import default
from flask import current_app

# Get the default credentials for the Cloud Run service account
#creds, project = default()

SERVICE_ACCOUNT_FILE = os.getenv('GCP_SERVICE_ACCOUNT_KEY_PATH')
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)

# Build the drive service using the credentials
drive_service = build('drive', 'v3', credentials=creds)

DRIVE_FOLDER_ID = '14_AeV9n8Nt5pZNwuigD6aE_nwXoW8_aw'  # Drive folder ID from link

def upload_to_drive(file_name, file_data):
    file_metadata = {
        'name': file_name,
        'parents': [DRIVE_FOLDER_ID]
    }
    media = MediaIoBaseUpload(BytesIO(file_data), mimetype='image/jpeg')
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    return file.get('id')
