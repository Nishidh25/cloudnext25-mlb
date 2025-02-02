## Cloud Run Function to send Gmail/drafts to users




Deploy this to Cloud Run - Functions

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

gcloud functions deploy email-service-function --gen2 --region=asia-south1 --runtime=python312 --source=. --entry-point=send_email --trigger-http --allow-unauthenticated

or

Deploy using TeraForm: https://cloud.google.com/functions/docs/samples/functions-v2-basic