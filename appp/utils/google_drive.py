import os
from google.auth import default
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO
from google.oauth2 import service_account
from google.auth import default
from flask import current_app


# this file houses the function used in the upload route to upload taken images to a google drive folder for our viewing and user data analysis to see what kinds of things users are taking photos of

#creds, project = default()

#SERVICE_ACCOUNT_FILE = os.getenv('GCP_SERVICE_ACCOUNT_KEY_PATH')
#creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)

def get_credentials():
    # Use default credentials when deployed
    try:
        creds, project = default()
        return creds
    except Exception as e:
        # fallback to service account key file locally
        SERVICE_ACCOUNT_FILE = os.getenv('GCP_SERVICE_ACCOUNT_KEY_PATH')
        creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
        return creds

drive_service = build('drive', 'v3', credentials= get_credentials())

DRIVE_FOLDER_ID = '14_AeV9n8Nt5pZNwuigD6aE_nwXoW8_aw'  # Drive folder ID accessed from folder link
                                                       # This folder houses the images

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
