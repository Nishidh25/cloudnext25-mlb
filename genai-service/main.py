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

from live_commentary import get_last_game_id,get_game_content,process_timestamp,get_game_timestamps,get_highlights_for_team,get_basic_player_info,is_not_json
from email_helper import make_authorized_get_request

from gcs_helper import upload_to_gcs,download_from_gcs
from langchain_gemini_helper import download_image

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
    language:str
    persona:str


class personalized_digest_response_model(BaseModel):
    status: str
    response: str
    gcs_url: str


class summarize_model(BaseModel):
    response: str
    language: str
    persona:str

vertexai.init(project=os.getenv("project_id",'mlb-hackathon-448812'), location="us-central1")

safety_settings = {
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
}

gemini_model = ChatVertexAI(
    model="gemini-2.0-flash-exp",
    temperature=0.8,
    top_p=0.95,
    max_tokens=None,
    max_retries=5,
    stop=None,
    safety_settings=safety_settings,
    response_mime_type= "application/json",
    response_schema={"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
        "personalized_title": {"type": "STRING",}, 
        "personalized_message_header": {"type": "STRING",},
        "personalized_digest": {"type": "STRING"}, 
        }, 
        "required": ["personalized_title", "personalized_message_header", "personalized_digest"]}
    }
    )


gemini_model_summary = ChatVertexAI(
    model="gemini-2.0-flash-exp",
    temperature=0.8,
    top_p=0.95,
    max_tokens=None,
    max_retries=5,
    stop=None,
    safety_settings=safety_settings
    )


system_prompt = SystemMessage(content="You are an MLB content creator, tasked to create personalized digests for fans based on the information provided.")


system_prompt_summary = SystemMessage(content="You are an MLB content creator, tasked to summarize player or team info for fans based on the information provided.")

def get_highlights_for_player(player_id,match_id=None):
    last_game_id,last_game_date = get_last_game_id(player_id)
    basic_info = get_basic_player_info(player_id)
    player_info = basic_info['people'][0]
    
    game_timestamps = get_game_timestamps(last_game_id)
    print("\nGame Timestamps:", len(game_timestamps))
    
    
    big_event_pitch_codes = [
        "E", "Z", "X", "D", "Y", "J",  # Run-scoring and play-determining
        "H", "I", "VB",                # Hit-by-pitch & intentional walks
        "1", "2", "3", "+1", "+2", "+3",  # Pickoff attempts
        "VP", "VC", "VS", "AC", "AB"   # Rule violations
    ]

    # Run in parallel and store results
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(process_timestamp, [last_game_id]*len(game_timestamps),game_timestamps))

    # Convert results to a DataFrame
    df = pd.DataFrame(results)
    filtered_df = []
    filtered_df = df[(df['batter_id'] == int(player_id)) | (df['pitcher_id'] == int(player_id)) & (df['pitch_code'].isin(big_event_pitch_codes))]
    # Filter out rows where `play_id` is JSON-like (string)
    filtered_df = filtered_df[filtered_df['play_id'].apply(is_not_json)]
    play_id = max(filtered_df['play_id'])
    filtered_df = filtered_df.drop(columns=['play_id'])
    
    # Display the DataFrame
    if filtered_df is []:
        print(filtered_df)
    
    
    return {
        'player_name': player_info['fullName'],
        'first_name': player_info['firstName'],
        'last_name' : player_info['lastName'],
        'age' : player_info['currentAge'],
        'position' : player_info['primaryPosition']['name'],
        'timestamp_df': df.to_string(),
        'playId': play_id
    }


@app.post("/summarize/",response_model=summarize_model)
async def personalized_digest(input: summarize_model,username: str = Depends(get_current_username)):
    
    summarize_prompt = f"""
    Give your output in this language: {input.language}
    The MLB fans persona is: {input.persona}
    Summarize this info: {input.response}
    """
    
    human_prompt = HumanMessage(
            content=[
                {"type": "text",
                "text": summarize_prompt
                }
            ],
        )
    
    combined_prompt = [
        system_prompt_summary,
        human_prompt
    ]
    
    response = gemini_model_summary.invoke(combined_prompt)
    
    return {
        "response": response.content,
        "language": input.language,
        "persona": input.persona
    }



@app.post("/personalized_digest/",response_model=personalized_digest_response_model)
async def personalized_digest(input: personalized_digest_input_model,username: str = Depends(get_current_username)):
    
    
    # Step 1: get subscribed info from sql/pub sub/api call
    email = input.email
    firstName = input.firstName 
    familyName = input.familyName
    playerId = input.playerId
    teamId = input.teamId
    language = input.language
    persona = input.persona
    
    
    
    # Step 2: get realtime details/image of any match / latest feeds from subscribed player/team
    
    #team = '133'
    #player = '669620'
    
    if playerId != "":
        player_details = get_highlights_for_player(playerId)
        personalized_prompt = f"""
        
        You are tasked to create a fresh new digest for {firstName} {familyName}, a fan of MLB Player {player_details['player_name']}, position {player_details['position']},current age {player_details['age']}
        The fans Persona is {persona}, do not mention this in the Output, use his persona to personalise the digest.
        Give the all the output in this language: {language}
        
        The digest is based on their latest game where the timestamped event details are in this dataframe :
        {player_details['timestamp_df']}
        """
        image_url = ""
        play_id = player_details["playId"]
        
    if teamId != "":
        team_details = get_highlights_for_team(teamId)
        
        personalized_prompt = f"""
        You are tasked to create a fresh new digest for {firstName} {familyName}, a fan of MLB team {team_details['team_name']} ({team_details['team_abbreviation']})
        The fans Persona is {persona}, do not mention this in the output, use his persona to personalise the digest.
        The digest is based on their latest game where home team was {team_details['home_team']} and away team {team_details['away_team']}
        Give the all the output in this language: {language}

        Context for the digest: {team_details['headline']} , {team_details['body_content']} 
        """
        image_url = team_details['primary_image_url']
        play_id = ""
        
    
    
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
    list_response = json.loads(response.content)
    print(list_response)
    
    # Step 4: download and upload image/video code
    if image_url != "":
        # Example usage
        source_file_path = "./image.jpg"  # Replace with the local file path
        download_image(image_url,source_file_path)
        
        bucket_name = "mlb-objects"  # Replace with your GCS bucket name
        destination_blob_name = "images/image.jpg"  # The name/path you want the file to have in GCS
        gcs_url,blob_name = upload_to_gcs(bucket_name, source_file_path, destination_blob_name)
    else:
        destination_blob_name = blob_name = ""
    
    
    
    # Step 5: send email using endpoint
    
    
    email_data = {
        "sender": "shekhawatnishidh5@gmail.com", 
        "receiver": email,  
        "subject": list_response[0]["personalized_title"],  
        "first_name": firstName, 
        "last_name": familyName, 
        "body_header":  list_response[0]["personalized_message_header"], 
        "body_content": list_response[0]["personalized_digest"], 
        "language": language, 
        "media_url": destination_blob_name,
        "play_id": play_id
    }
    
    
    endpoint = os.getenv('email_service_url','')
    status = make_authorized_get_request(endpoint,email_data)
    
    return {
        "status":status,
        "response": response.content,
        "gcs_url": blob_name
    }