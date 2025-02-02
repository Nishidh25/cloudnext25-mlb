import os
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from functions_framework import http
from flask import Request as frequest
from google.cloud import storage


# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.send"
]



def download_blob(bucket_name, source_blob_name):
    """Downloads a blob from the bucket and returns its content as a string."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    content = blob.download_as_string()
    #print('content', content)
    return content.decode('utf-8')  # Assuming the file is UTF-8 encoded

def send_message(service, sender, receiver):
    """Send an email message through Gmail API"""
    try:
        message = EmailMessage()
        message.set_content("This is an automated draft mail")
        message["To"] = receiver
        message["From"] = sender
        message["Subject"] = "Automated draft"
        
        # Encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        create_message = {"raw": encoded_message}
        send_message = service.users().messages().send(userId="me", body=create_message).execute()
        
        return f'Message Id: {send_message["id"]}'
    
    except HttpError as error:
        return f"An error occurred: {error}"

def get_gmail_service():
    """Get the authenticated Gmail API service"""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES, redirect_uri="http://localhost:50236/"
            )
            creds = flow.run_local_server(port=50236)
        
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    
    return build("gmail", "v1", credentials=creds)

@http
def send_email(request):
    """Endpoint to send an email through Gmail API"""
    request_json = request.get_json(silent=True)
    print("request_json",request_json)
    request_args = request.args
    
    
    if request_json:
      sender = request_json.get('sender')
      receiver = request_json.get('receiver')

    if not sender or not receiver:
        return f'{{"error": "Sender and receiver email addresses are required."}}', 400

    try:
        service = get_gmail_service()
        message_id = send_message(service, sender, receiver)
        return f'{{"message": "{message_id}"}}', 200
    except Exception as e:
        return f'{{"error": "{str(e)}"}}', 500
