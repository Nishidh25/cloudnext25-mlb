import os
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import Annotated, Union
import asyncio
import secrets
from pydantic import BaseModel
import concurrent.futures
import pandas as pd
import json
import vertexai
import tempfile

from live_commentary import get_last_game_id,get_game_content,process_timestamp,get_game_timestamps,get_highlights_for_team
from email_helper import make_authorized_get_request

from langchain_google_vertexai import ChatVertexAI
from langchain_google_vertexai import VertexAI, HarmCategory, HarmBlockThreshold
from langchain_core.messages import HumanMessage, SystemMessage

app = FastAPI()
security = HTTPBasic()

## Since this is is test environment we can use basic credentials
## Production environment needs to have token based/secret manager based auth
## more details on how to implement this her: 
def get_current_username(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = os.getenv('api_username').encode("utf8")
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = os.getenv('api_password').encode("utf8")
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


class personalized_digest_input_model(BaseModel):
    email: str
    firstName: str
    familyName: str
    playerId:str
    teamId:str




# Get the credentials JSON string from the environment variable
creds_json = os.getenv('vertex_ai_service_acc')

# If the credentials are found
if creds_json:
    # Create a temporary file to store the credentials
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp_file:
        temp_file.write(creds_json)
        temp_file_path = temp_file.name
        
    # Set the GOOGLE_APPLICATION_CREDENTIALS environment variable to the path of the temp file
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_file_path
else:
    ## Code is for local running using creds file
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./vertex_ai_service_account.json"

vertexai.init(project=json.loads(creds_json)["project_id"], location="asia-south1")

safety_settings = {
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
}


gemini_model = ChatVertexAI(
    model="gemini-1.5-flash-002",
    temperature=0.8, #0.8
    top_p=0.95,
    max_tokens=None,
    max_retries=6,
    stop=None,
    safety_settings=safety_settings)

system_prompt = SystemMessage(content="You are an MLB content creator, tasked to create personalized digests for fans based on the information provided.")





class personalized_digest_response_model(BaseModel):
    status: str

def get_highlights_for_player(player_id,match_id=None):
    last_game_id,last_game_date = get_last_game_id(player_id)
    content = get_game_content(last_game_id)
    
    game_timestamps = get_game_timestamps(last_game_id)
    print("\nGame Timestamps:", len(game_timestamps))

    big_event_pitch_codes = {
        "E", "Z", "X", "D", "Y", "J",  # Run-scoring and play-determining
        "H", "I", "VB",                # Hit-by-pitch & intentional walks
        "1", "2", "3", "+1", "+2", "+3",  # Pickoff attempts
        "VP", "VC", "VS", "AC", "AB"   # Rule violations
    }

    # Run in parallel and store results
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(process_timestamp, game_timestamps))

    # Convert results to a DataFrame
    df = pd.DataFrame(results)

    # Display the DataFrame
    print(df)
    
    
    
    
    
    pass


@app.post("/personalized_digest/",response_model=personalized_digest_response_model)
async def personalized_digest(input: personalized_digest_input_model,username: str = Depends(get_current_username)):
    
    
    # Step 1: get subscribed info from sql/pub sub/api call
    email = input.email
    firstName = input.firstName 
    familyName = input.familyName
    playerId = input.playerId
    teamId = input.teamId
    
    
    # Step 2: get realtime details/image of any match / latest feeds from subscribed player/team
    
    #team = '133'
    #player = '669620'
    
    if playerId != "":
        player_details = get_highlights_for_player(playerId)
        personalized_prompt = f"""
        You are tasked to create a fresh new digest for {firstName} {familyName}, a fan of MLB team {player_details['team_name']} ({player_details['team_abbreviation']})
        
        The digest is based on their latest game where home team was {player_details['home_team']} and away team {player_details['away_team']}
        
        Context for the digest: {player_details['headline']} , {player_details['body']} 
        """
        
    if teamId != "":
        team_details = get_highlights_for_team(teamId)
        
        personalized_prompt = f"""
        You are tasked to create a fresh new digest for {firstName} {familyName}, a fan of MLB team {team_details['team_name']} ({team_details['team_abbreviation']})
        
        The digest is based on their latest game where home team was {team_details['home_team']} and away team {team_details['away_team']}
        
        Context for the digest: {team_details['headline']} , {team_details['body_content']} 
        """
        
    
    
    # Step 3: gemini to summarize the details
    
    human_prompt = HumanMessage(
            content=[
                {"type": "text",
                "text": personalized_prompt
                }
            ],
        )
    
    combined_prompt = [
        system_prompt,
        human_prompt
    ]
    response = gemini_model.invoke(combined_prompt)
    print(response)
    
    # Step 4: VEO to generate the image/video code
    
    
    # Step 5: send email using endpoint
    
    
    email_data = {
        'sender':'shekhawatnishidh5@gmail.com',
        'receiver':email
    }
    endpoint = 'https://asia-south1-mlb-hackathon-448812.cloudfunctions.net/email-service-function'
    status = make_authorized_get_request(endpoint,email_data)
    
    return {
        "status":status,
        "response": response
    }