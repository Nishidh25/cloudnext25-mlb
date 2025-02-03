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

import base64
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email import encoders


# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.send"
]


def download_from_gcs(bucket_name, source_blob_name, destination_file_path):
    """Downloads a blob from the bucket and returns its content as a string."""
    storage_client = storage.Client()
    
    # Get the bucket object
    bucket = storage_client.get_bucket(bucket_name)

    # Get the blob (file) from the bucket
    blob = bucket.blob(source_blob_name)

    # Download the file to the local system
    blob.download_to_filename(destination_file_path)

    return destination_file_path



def send_message(service, sender, receiver, subject, first_name, last_name, body_header, body_content, language = "English",media_path=None,single_play_url=None):
    """Send an email message through Gmail API with an inline image or GIF, formatted HTML body, and footer"""
    try:
        # Create the MIME message
        message = MIMEMultipart("related")
        message["To"] = receiver
        message["From"] = sender
        message["Subject"] = subject

        if language == "Spanish":
          hey = "Hola,"
          fan_community = "Actualizaciones de la Comunidad de Fans"
          fan_community_description = "¡Únete a la conversación con otros fanáticos! Mira las últimas discusiones, encuestas y envíos de los fans."
          fan_community_button = "Unirse a la Conversación"
          clips_of_play = "Ver clips de la obra"

          visit_mlb = "Visita Mi MLB"
          
          footer_modify = "Estás recibiendo este correo electrónico porque te registraste en nuestro MLB Fan Digest. Si deseas cancelar la suscripción o modificarla "
          click_here = "haz clic aquí"
          footer_poweredby = "Este resumen te lo trae Google Cloud - Gemini 2.0."
        elif language == "Japanese":
          hey = "こんにちは、"
          fan_community = "ファンコミュニティの更新情報"
          fan_community_description = "他のファンとの会話に参加しよう！最新のディスカッション、投票、ファンからの投稿をチェックしてみてください。"
          fan_community_button = "ディスカッションに参加する"
          clips_of_play = "劇のクリップを見る"

          visit_mlb = "私のMLBを訪問"
          
          footer_modify = "このメールは、MLB Fan Digestに登録したために受信しています。購読を解除したり、設定を変更したりするには "
          click_here = "こちらをクリック"
          footer_poweredby = "このダイジェストはGoogle Cloud - Gemini 2.0によって提供されています。"
        else:
          hey = "Hey,"
          fan_community = "Fan Community Updates"
          fan_community_description = "Join the conversation with other fans! Check out the latest discussions, polls, and fan submissions."
          fan_community_button = "Join the Discussion"
          clips_of_play = "View Clips of the play"
          
          visit_mlb = "Visit My MLB"

          footer_modify = "You're receiving this email because you signed up for our MLB Fan Digest. If you'd like to unsubscribe or modify subscriptions "
          click_here = "click here"
          footer_poweredby = "This digest is Powered to you by Google Cloud - Gemini 2.0."
        
              


        # HTML body with dynamic content and embedded media
         # HTML body with dynamic content and embedded media (image or gif)
        html_body = f"""
        <html>
          <head>
            <style>
              body {{
                font-family: Arial, sans-serif;
                color: #333;
                background-color: #f7f7f7;
                margin: 0;
                padding: 0;
              }}
              .container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
              }}
              h1 {{
                color: #003b5c;
                font-size: 28px;
                text-align: center;
                margin-bottom: 20px;
              }}
              h2 {{
                color: #333;
                font-size: 22px;
                margin-bottom: 10px;
              }}
              p {{
                font-size: 16px;
                line-height: 1.6;
                color: #555;
              }}
              .cta-button {{
                background-color: #0052cc;
                color: #ffffff !important;  /* Ensure the text stays white */
                padding: 10px 20px;
                border-radius: 5px;
                text-decoration: none;
                display: inline-block;
                font-weight: bold;
                margin-top: 20px;
                text-align: center;  /* Ensures any link text is aligned properly */
                }}
                .cta-button:hover {{
                background-color: #003a99;
                }}
                .cta-button:link, .cta-button:visited {{
                color: #ffffff !important;  /* Override default link color (blue) */
                }}
                .cta-button:active, .cta-button:hover {{
                color: #ffffff !important;  /* Ensure color stays white on active or hover */
                }}
              .footer {{
                font-size: 8px;
                text-align: center;
                color: #888;
                margin-top: 30px;
              }}
              .footer a {{
                color: #0052cc;
                text-decoration: none;
              }}
              .footer a:hover {{
                text-decoration: underline;
              }}
              .image-container {{
                text-align: center;
                margin-top: 20px;
              }}
              img {{
                width: 100%;
                max-width: 400px;
                height: auto;
                border-radius: 8px;
              }}
            </style>
          </head>
          <body>
            <div class="container">
              <h1>{hey} {first_name}!</h1>
              
              <h2>{body_header}</h2>
              {f'<div class="image-container"><img src="cid:my_media" alt="Highlight" /></div>' if media_path else ''}
              <p>{body_content}</p>
              {f"<div style='text-align: center;'><a href='{single_play_url}' class='cta-button'>{clips_of_play}</a></div>" if single_play_url else''}
              <h2>{fan_community}</h2>
              <p>{fan_community_description}</p>
              <div style="text-align: center;">
              <a href="https://www.mlb.com/fans" class="cta-button">{fan_community_button}</a>
              <a href="https://mlb-frontend-service-513391239750.asia-south1.run.app" class="cta-button">{visit_mlb}</a>
              </div>

              <div class="footer">
                <p>{footer_modify}<a href="https://mlb-frontend-service-513391239750.asia-south1.run.app">{click_here}</a>.</p>
                <p>{footer_poweredby}</p>
              </div>
            </div>
          </body>
        </html>
        """
        
        # Attach HTML body
        html_part = MIMEText(html_body, "html")
        message.attach(html_part)

        # Attach media (image or gif) inline if provided
        if media_path:
            with open(media_path, "rb") as media_file:
                media = MIMEImage(media_file.read())  # Handles both images and gifs
                media.add_header("Content-ID", "<my_media>")  # Match with cid in HTML
                media.add_header("Content-Disposition", "inline", filename=media_path.split('/')[-1])
                message.attach(media)

        # Encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Send the email via Gmail API
        create_message = {"raw": encoded_message}
        send_message = service.users().messages().send(userId="me", body=create_message).execute()

        return f'Message Id: {send_message["id"]}'

    except Exception as e:
        return f"An error occurred: {str(e)}"

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
        subject = request_json.get('subject')
        first_name = request_json.get('first_name')
        last_name = request_json.get('last_name')
        body_header = request_json.get('body_header')
        body_content = request_json.get('body_content')
        language = request_json.get('language')
        media_url = request_json.get('media_url')
        play_id = request_json.get('play_id')

    if not sender or not receiver:
        return f'{{"error": "Sender and receiver email addresses are required."}}', 400
      
    if media_url != "":
      media_path = download_from_gcs('mlb-objects',media_url,"./image.jpg")
    else:
      media_path = None

    if play_id != "":
      single_play_url = f'https://www.mlb.com/video/search?q=playid=\"{play_id}\"'
    else:
      single_play_url = None
      
    try:
        service = get_gmail_service()
        message_id = send_message(service, sender, receiver, subject, first_name,last_name,body_header,body_content,language,media_path,single_play_url)

        return f'{{"message": "{message_id}"}}', 200
    except Exception as e:
        return f'{{"error": "{str(e)}"}}', 500
