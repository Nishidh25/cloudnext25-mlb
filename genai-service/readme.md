# Service 2 - Gen AI Service: FastAPI 
## Overview

This FastAPI service provides two main functionalities using Vertex AI Gemini 2.0:

1. **Summarize Endpoint**: Personalizes information and returns a summarized response based on input data.
2. **Personalized Digest Endpoint**: Sends subscription-based email digests tailored to either player or team subscriptions, taking care of language preferences.

The **Personalized Digest** service uses the MLB API, as defined in helper functions, to fetch data and personalize the digest content based on the player or team subscription, focusing on the most recent match of the 2024 season.
This data is then processed and personalized to the subscriber's preferences.

Helper functions are defined within the service to interact with the MLB API, retrieving the required match details based on the provided player or team information.

---

## How was MLB API Used
MLB API Data used for getting realtime events, specifically last game events and Articles/Content: (All defined in genai-service/live_commentary.py)

Getting Player Stats "https://statsapi.mlb.com/api/v1/people/{person_id}/stats"

Getting Game Highlights "https://statsapi.mlb.com/api/v1/game/{game_pk}/content" for Team Highlights of last game

Getting Temestamps to get live feed of a game for that timestamp "https://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live/timestamps"

Getting Game Live Feed "https://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live" for Event level Highlights of last game , which is filtred by player id to get player digest/highlights. PlayId Video is also extracted from these events


---
## Gen AI Service API Endpoints

### 1. **/summarize/**

- **Method**: `POST`
- **Summary**: Personalizes information and returns a summary of the provided data.
- **Request Body**: Expects a JSON payload with the following structure:
  
  ```json
  {
    "response": "Your response message",
    "language": "English",
    "persona": "player" or "team"
  }
  ```

### 2. **/summarize/**

- **Method**: `POST`
- **Summary**: Sends a personalized digest based on either Player or Team subscription to the user email.
- **Request Body**: Expects a JSON payload with the following structure:

For a Team Digest Email, playerId needs to be ""
```json
{
  "email": "shekhawatnishidh5@gmail.com",
  "firstName": "Nishidh",
  "familyName": "Shekhawat",
  "playerId": "",
  "teamId": "133",
  "language": "English", or 'Spanish' or 'Japanese'
  "persona": "The College Student Fan"
}
```

For a Player Digest Email, teamId needs to be ""
```json
{
  "email": "shekhawatnishidh5@gmail.com",
  "firstName": "Nishidh",
  "familyName": "Shekhawat",
  "playerId": "67890",
  "teamId": "",
  "language": "English", or 'Spanish' or 'Japanese'
  "persona": "The College Student Fan"
}
```



## Deployment 

Define the Environment variables like Vertex AI keys and others in the deploy.sh of the master peroject.

If you want to deploy individually then use  ```sh deploy.sh```

Make sure your Artifact Registery and Cloud Run is Set up properly

