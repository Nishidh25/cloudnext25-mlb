script:
    - gcloud auth configure-docker
    - gcloud builds submit --tag asia-south1-docker.pkg.dev/mlb-hackathon-448812/mlb-ai-service/mbl-ai-service-api:LATEST
    - gcloud run deploy audio-feedback-api --image asia-south1-docker.pkg.dev/mlb-hackathon-448812/mlb-ai-service/mbl-ai-service-api:LATEST --region asia-south1 --platform managed --allow-unauthenticated


gcloud run deploy sample --port 8080 --source .

  
