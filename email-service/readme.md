# Service 3: Gmail Service - Cloud Run Function

This service leverages the Gmail Python API to send emails directly from the authenticated user's Gmail account. It is deployed as a Cloud Function, designed to serve as a simple HTTP endpoint that can be easily integrated and called by other services.

Sample Email Digests: 

2 Types: Team Digest(with Images) , Player Digests(with Players)

<img src="/images/gmail-team_digest_english.png" width="400"/> <img src="/images/gmail-player_digest_english.png" width="400"/>


## Features

- Sends emails or drafts from the logged-in user's Gmail account.
- Ability to attach Images and Media in email
- Deployed on Cloud Run for scalability and ease of integration.
- English, Spanish and Japanese Languages 
- Can be accessed by other services to trigger email sending functionality.

## Sample Curl Request:
```
curl -X POST \
  'https://<YOUR_CLOUD_FUNCTION_URL>' \
  -H 'Content-Type: application/json' \
  -d '{
        "sender": "<sender_value>",
        "receiver": "<receiver_value>",
        "subject": "<subject_value>",
        "first_name": "<first_name_value>",
        "last_name": "<last_name_value>",
        "body_header": "<body_header_value>",
        "body_content": "<body_content_value>",
        "language": "<language_value>",
        "media_url": "<media_url_value>",
        "play_id": "<play_id_value>"
      }'

```

## Pre-deployment : Initial Setup
This service requires manual run before deployment if you do not have a Google Workspace account

1. Setup OAuth in Google Cloud and download credentials.json [Google Help](https://support.google.com/cloud/answer/6158849?hl=en)
2. Run the code ```python main.py``` ,  it wil open a url. Make sure to add this url to your redirect uri in console
3. Login using your google account
4. A token.json will be generated in the same path
5. Now it is ready for deployment

## Deploy to Cloud Run - Functions

Using GCLOUD CLI:
```
gcloud functions deploy email-service-function 
  --gen2 
  --region=asia-south1 
  --runtime=python312 
  --source=. 
  --entry-point=send_email 
  --trigger-http
  --allow-unauthenticated
```

or 

```gcloud functions deploy email-service-function --gen2 --region=asia-south1 --runtime=python312 --source=. --entry-point=send_email --trigger-http --allow-unauthenticated```

or 

[Deploy using TeraForm](https://cloud.google.com/functions/docs/samples/functions-v2-basic)
