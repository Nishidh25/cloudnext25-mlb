#!/bin/bash

#Google SSO Credentials
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# Cloud SQL Postgres Credentials
instance_connection_name= # e.g. 'project:region:instance'
db_user=
db_pass=
db_name=postgres
SECRET_KEY=a_very_secret_key # Any text or key will do

# Credentials for Gen AI API Service
api_username=
api_password=

# Credentaials for Email Service
gcloud secrets create vertex_ai_service_acc --data-file=./vertex_ai_service_account.json
gcloud secrets create email_sso_creds --data-file=./email-service/email_sso_credentials.json



# Service endpoint urls
# For services to communicate with each other , instead of hardcoding, keeping them in a secret
genai_api_service_url=https:// # Url for api service, add this once api service is deployed
email_service_url=https://{url}/email-service-function # Url for email cloud function, add this once email function is deployed


# Loop through the variable names and create secrets
for var in GOOGLE_CLIENT_ID GOOGLE_CLIENT_SECRET instance_connection_name db_user db_pass db_name SECRET_KEY genai_api_service_url email_service_url api_username api_password; do
  # Get the value of the variable using eval
  value=$(eval echo \$$var)
  
  # Create a secret in Google Cloud Secret Manager
  printf "%s" "$value" | gcloud secrets create "$var" --data-file=-
done