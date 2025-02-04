gcloud functions deploy email-service-function --gen2 --region=asia-south1 --runtime=python312 --source=. --entry-point=send_email --trigger-http
