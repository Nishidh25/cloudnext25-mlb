import os
import gradio as gr
from fastapi import FastAPI, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.config import Config
from authlib.integrations.starlette_client import OAuth
from pydantic import BaseModel
from urllib.parse import urlparse, urlunparse
from mlb_api_wrapper import get_teams,get_team_roster,get_team_logo_url,get_player_headshot_from_url,get_team_basic_details,get_player_details_page_data
from database import session
from database.orm import orm_create_user,orm_subscribe_user

from genai_service_helper import call_personalized_digest,call_summarize


## Fast API wrapped with gradio for security
app = FastAPI()
origins = [
    "*",
]

SECRET_KEY = os.getenv('SECRET_KEY','a_very_secret_key')

app.add_middleware(
    SessionMiddleware, 
    secret_key=SECRET_KEY
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"], #"*.nishidh.online"
)

#app.add_middleware(HTTPSRedirectMiddleware)

CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'

# Initialize OAuth2
oauth = OAuth()
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_id= os.getenv("GOOGLE_CLIENT_ID"),
    client_secret= os.getenv("GOOGLE_CLIENT_SECRET"),
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account'
        }
    )


# Dependency to get the current user
def get_user(request: Request):
    user = request.session.get('user')
    if user:
        #print("Logged in user: ",user)
        return user['email'] #email,name,preferred_username,oid
    return None


@app.get('/')
def public(user: dict = Depends(get_user)):
    if user:
        #redirect_url = request.url_for('event_msg').include_query_params(msg="Succesfully created!")
        return RedirectResponse(url='/home') #RedirectResponse(url=redirect_url)
    else:
        return RedirectResponse(url='/signin')
    

@app.route('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')


@app.route('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    # If your app is running on https, you should ensure that the
    # `redirect_uri` is https, e.g. uncomment the following lines:
    redirect_uri = urlunparse(urlparse(str(redirect_uri))._replace(scheme='https'))
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.route('/auth')
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        print("access_token")
        user = token.get('userinfo')
        if user:
            request.session['user'] = user
            orm_create_user(session, email=request.session['user']['email'], first_name=request.session['user']['given_name'], last_name=request.session['user']['family_name'])
    except Exception as e:
        print("OAuthError",str(e))
        return RedirectResponse(url='/')
    return RedirectResponse(url='/')


@app.route('/logout')
async def logout(request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')

class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: str = "OK"
    

@app.get(
    "/health",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
def get_health() -> HealthCheck:
    """
    ## Perform a Health Check
    Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
    to ensure a robust container orchestration and management is in place. Other
    services which rely on proper functioning of the API service will not deploy if this
    endpoint returns any other HTTP status code except 200 (OK).
    Returns:
        HealthCheck: Returns a JSON response with the health status
    """
    return HealthCheck(status="OK")



def get_user_email(request: gr.Request):
    return request.username

def get_user_names(request: gr.Request):
    return request.session['user']['given_name'],request.session['user']['family_name']

def get_user_greeting(request: gr.Request):
    first_name, last_name = request.session['user']['given_name'],request.session['user']['family_name']

    return  f"## Welcome to My MLB Digest, {first_name}!"



js_login="""
() => {

            document.getElementsByClassName("show-api")[0].style.visibility = 'hidden';
            //document.getElementsByClassName("built-with")[0].style.visibility = 'hidden';
            document.getElementsByClassName("built-with")[0].href=".";
            document.getElementsByClassName("built-with")[0].textContent="Built on Vertex AI";
            document.getElementsByClassName("built-with")[0].target="";
            
            // Remove the entire footer
            var el=document.querySelector('footer');
            el.parentNode.removeChild(el);
            
        }
"""

with gr.Blocks(fill_width=True,js=js_login,title="My MLB") as demo:
    with gr.Row(variant="Headers",visible=True,equal_height=True) as header:
        with gr.Column():
            welcome = gr.Markdown("# Welcome to My MLB Digest")
            demo.load(get_user_greeting, outputs=welcome)
            #gr.Image('./src/logo_v2.png',container=False,show_download_button=False,height=0, width=150,scale=0,min_width=300,show_fullscreen_button=False)
        
        with gr.Column():
            with gr.Row():
                gr.HTML("""<div id='logout_button' style='display:block; float: right;></div>""")
                greeting= gr.Markdown(elem_id="logout_button")
                #user_info = gr.components.HTML()
                logout_btn=gr.Button("|  Logout", link="/logout",elem_id="logout_button",icon="./images/logout.png",min_width=150,scale=0)
    
    with gr.Tab("Subscribe"):
        with gr.Row() as player_selector:
            with gr.Column() as sideBar:
                intro = gr.Markdown("#### 1. Start Selecting these options to personalize your fan digest")
                selection_season = gr.Dropdown(choices=['2023','2024','2025'], label="Season dropdown",value=[''])
                selection_team = gr.Dropdown(choices=[], label="Select your Team")
                selection_player = gr.Dropdown([],label="Select your player")
                selection_language = gr.Dropdown(choices=['English','Spanish','Japanese'], label="Select your language",value='English')
                selection_persona = gr.Dropdown(choices= ['None',"The Stat Buff","The Superstitious Fan","The Nostalgic Fan","The Fair-Weather Fan","The Ultimate Tailgater","The Hardcore Loyalist","The Young Enthusiast","The Millennial Die-Hard","The College Student Fan"], label="What persona are you?",allow_custom_value=True,interactive=True)
                personalize_data = gr.Button("Personalize using Gemini 2.0", variant="huggingface", icon = './images/google-gemini-icon.jpg')
                
            
                def get_teams_from_season(season):
                    teams_data = get_teams(season=season,active_status="Y",sport_id=1)
                    print(teams_data)
                    if teams_data:
                        print(f"Teams in the {season} season:")
                        teams = teams_data.get('teams', [])
                        team_dict = [(team.get('name'),team.get('id')) for team in teams]
                    return gr.update(choices=team_dict) 
                
                def get_players_from_teams_season(season,team_id):
                    roster_data = get_team_roster(team_id, season)
                    if roster_data:
                        print(f"Roster for team ID {team_id} in {season}:")
                        roster = roster_data.get('roster', [])
                        player_dict = [(player.get('person', {}).get('fullName', 'N/A'), player.get('person', {}).get('id', 'N/A')) for player in roster]
                    else:
                        print("Could not retrieve roster information.")
                        
                    print(player_dict)
                    return gr.update(choices=player_dict) 
            
            

            with gr.Column() as team_details:
                intro_team = gr.Markdown("#### 2. Subscribe to get gmail digests for this team")
                with gr.Row():
                    team_logo = gr.Image(scale=0.25,show_label=False,show_download_button=False,show_fullscreen_button=False, height= 200,width=200)
                    team_details = gr.Markdown("""## Team Details
                                               Select a team from the dropdown to start viewing their info
                                               """)
                with gr.Row():
                    subscribe_to_team = gr.Button("Subscribe to Team Digest", variant="primary",icon = './images/google-gemini-icon.jpg')
            
            with gr.Column() as player_details:
                intro_player = gr.Markdown("#### 3. Subscribe to get gmail digests for this player")
                with gr.Row():
                    player_headshot = gr.Image(scale=0.25,show_label=False,show_download_button=False,show_fullscreen_button=False, height= 200,width=200)
                    player_details = gr.Markdown(""" ## Player Details
                                                Select a player from the dropdown to start viewing his stats 
                                                """)
                with gr.Row():
                    subscribe_to_player = gr.Button("Subscribe to Player Digest", variant="primary",icon = './images/google-gemini-icon.jpg')
            
                with gr.Row():            
                    text_email = gr.Textbox(visible=False)
                    user_first_name = gr.Textbox(visible=False)
                    user_last_name = gr.Textbox(visible=False)
                    demo.load(get_user_email, outputs=text_email)
                    demo.load(get_user_names, outputs=[user_first_name,user_last_name])
                    empty_textbox = gr.Textbox("",visible=False)
        
        selection_season.input(get_teams_from_season, selection_season, selection_team)
        
        def update_get_team_logo_url(team_id):
            return gr.update(value = get_team_logo_url(team_id))    
        
        def update_get_player_headshot_from_url(person_id):
            return gr.update(value = get_player_headshot_from_url(person_id))    
        
        def update_image_url_to_default():
            return gr.update(value = None)   
        
        def update_get_team_basic_details(team_id):
            team_name,team_abbreviation,team_location,manager = get_team_basic_details(team_id)
            
            markdown_text  =  f"""
            ## Team Details
            
            **Team Name**: {team_name}
            
            **Team Abbreviation**: {team_abbreviation}
            
            **Team Location**: {team_location}
            
            **Manager**: {manager}
            """
            return markdown_text
        
        selection_team.input(
            get_players_from_teams_season, [selection_season,selection_team], selection_player
            ).then(
                update_get_team_logo_url,[selection_team],team_logo
            ).then(
                update_get_team_basic_details,[selection_team],team_details
            ).then(
                update_image_url_to_default,None,player_headshot
            )

        selection_player.input(
                update_get_player_headshot_from_url,[selection_player],player_headshot
            ).then(
                get_player_details_page_data,[selection_player],player_details 
            )
        
        
        def update_orm_subscribe_user(text_email, user_first_name, user_last_name, selection_team, selection_player):
            orm_subscribe_user(session,text_email, user_first_name, user_last_name, str(selection_team), str(selection_player))
            gr.Info(f"You have subscribed to this Team/Player. You will start receiving the emails on your logged in email id:{text_email}")
            
        subscribe_to_team.click(
            update_orm_subscribe_user, inputs=[text_email, user_first_name, user_last_name, selection_team, selection_player]
            ).then(
                call_personalized_digest, inputs=[text_email, user_first_name,user_last_name, empty_textbox, selection_team, selection_language,selection_persona],outputs=None
            )
            
        subscribe_to_player.click(
            update_orm_subscribe_user, inputs=[text_email, user_first_name, user_last_name, selection_team, selection_player]
            ).then(
                call_personalized_digest, inputs=[text_email, user_first_name,user_last_name, selection_player, empty_textbox, selection_language,selection_persona],outputs=None
            )
            
        personalize_data.click(
            call_summarize,inputs=[team_details,selection_language,selection_persona], outputs=[team_details]
        ).then(
            call_summarize,inputs=[player_details,selection_language,selection_persona], outputs=[player_details]
        )
    with gr.Tab("View Subscriptions"):
        gr.Markdown("## Your Subscriptions will appear here")
        #create_user = orm_create_user(session) 
        


css_login="""
footer {visibility: visible;
}
h1 {
    text-align: center;
    display:block;
}
h5 {
    text-align: center;
    display:block;
}
#loginsso {
  height: 50px; /* Adjust to match the Google login button size */
  background:#4285F4; /* Google colors gradient */
  color: white;
  text-align: center;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 5px; /* Rounded corners */
  padding: 0 20px; /* Horizontal padding */
  font-size: 16px;
  font-weight: bold;
  cursor: pointer; /* Makes it clickable */
  border: none; /* Remove any default border */
}

#loginsso img {
  width: 24px; /* Adjust icon size */
  height: 24px;
  margin-right: 10px; /* Space between the icon and text */
  vertical-align: middle;
}
#logo {
    display: flex;
    justify-content: center;  /* Horizontally center the image */
    align-items: center;      /* Vertically center the image */
    width: 100%;              /* Ensure the div takes up the full width */
    height: 100%;             /* Ensure the div takes up the full height */
}
"""

js_d="""
() => {
            document.body.classList.toggle('dark');
        }
"""

with gr.Blocks(fill_width=True,css=css_login,js=js_login,title="My MLB") as signin:
    with gr.Row():
        space= gr.HTML("""<br><br><br><br>""")  
    with gr.Row():
        with gr.Column(scale=1):
            pass
        with gr.Column(variant="panel",scale=2):
            gr.Markdown("""<h1 style="font-family: 'Roboto Mono', monospace;">My MLB</h1>""")
            gr.Markdown("""<h5 style="font-family: 'Roboto Mono', monospace;">Your One Stop for Personalized Digests</h5>""")
            
            #gr.HTML("""<div id='logo' style='display:block; margin:auto; width:150px;text-align: center;'></div>""")
            gr.Image('./images/cloud_x_mlb_logo.png',container=False,show_download_button=False,show_fullscreen_button=False,elem_id='logo')

        with gr.Column(scale=1):
            pass
    with gr.Row():
        with gr.Column(scale=1):
            pass
        with gr.Column(scale=2):
            gr.Button("  Login with Google", link="/login",icon='./images/google.png',elem_id="loginsso")
        with gr.Column(scale=1):
            pass

app = gr.mount_gradio_app(app, signin, path="/signin",favicon_path='./images/favicon.ico',allowed_paths=["./src/"])

app = gr.mount_gradio_app(app, demo.queue(), path="/home",allowed_paths=["./"],favicon_path='./images/favicon.ico',auth_dependency=get_user)