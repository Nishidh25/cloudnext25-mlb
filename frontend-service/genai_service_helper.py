import requests
from requests.auth import HTTPBasicAuth
import gradio as gr
import os

# Base URL for your API (replace with the actual URL of your FastAPI server)
base_url = os.getenv('genai_api_service_url','')
api_username = os.getenv('api_username')
api_password = os.getenv('api_password')

basic_auth = HTTPBasicAuth(api_username, api_password)

 # Set the headers as required by the API
headers = {
    "accept": "application/json",  # The accept header
    "Content-Type": "application/json"  # The Content-Type header
}

# Function to call personalized_digest endpoint
def call_personalized_digest(email: str, firstName: str, familyName: str, playerId: str, teamId: str, language: str,persona: str):
    url = f"{base_url}/personalized_digest/"  # Adjust the endpoint if needed
    
    # Prepare the data as a dictionary
    data = {
        "email": email,
        "firstName": firstName,
        "familyName": familyName,
        "playerId": str(playerId),
        "teamId": str(teamId),
        "language": language,
        "persona": persona
    }
    
    # Send the request
    gr.Info("You will receive an email digest shortly")
    response = requests.post(url, json=data,auth=basic_auth,headers=headers)
    
    if response.status_code == 200:
        return response.json()  # Return JSON response
    else:
        print("Error:", response.status_code, response.text)
        raise gr.Error("There was some error while fetching the details from MLB API, please slect another player or team and try again.")

# Function to call summarize endpoint
def call_summarize(response_text: str, language: str,persona: str):
    url = f"{base_url}/summarize/"  # Adjust the endpoint if needed
    
    # Prepare the data as a dictionary
    data = {
        "response": response_text,
        "language": language,
        "persona": persona
    }
    
    # Send the request
    response = requests.post(url, json=data,auth = basic_auth,headers=headers)
    
    if response.status_code == 200:
        return response.json()['response']  # Return JSON response
    else:
        print("Error:", response.status_code, response.text)
        gr.Info("There was some error while summarising these details, make sure you have selected the Language and all other Parameters")
        return response_text