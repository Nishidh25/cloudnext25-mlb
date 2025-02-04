# Service 1 - Frontend Service : Cloud Run Service

Frotend is built in Gradio with Google OAuth.

The job of the Frontend is to Make the functionality easily accessable to the user in an Interactive way.

Python Gradio was used as it is Quick to build and easy to manage and is built with AI use cases in mind.


<img src="/images/signin_light_theme.png" width="400"/>                             <img src="/images/home_light_theme.png" width="400"/> 




## How was MLB API Used:
MLB API Data used for populating basic filds throughout the UI: (All defined in mlb_api_wrapper.py)

Getting Team Details: http://statsapi.mlb.com/api/v1/teams/{team_id}

Getting Player Details: https://statsapi.mlb.com/api/v1/people/{person_id}

Getting Team Logo: https://www.mlbstatic.com/team-logos/{team_id}.svg"

Getting PLayer Logo: https://img.mlbstatic.com/mlb-photos/image/upload/w_213,d_people:generic::headshot:silo:current.png,q_auto:best,f_auto/v1/people/{person_id}/headshot/67/current


## Connections with other services
Frontend Service is connected to Private CLoud SQL (potgres) using Serverless VPC connector (cloud sql connector is in ./database)

Frontend Service is connected Gen AI Service 2 - API called within gradio functions (genai_service_helper.py)

## Deploy

Deployment Script is already loaded.

```sh deploy.sh```

Configure cloud SQL and Serverless VPC Connector. If there is any issue with Cloud SQL and VPC connecor. This Service will not start and fail in deployment (Timeput Error)
