import requests
import json

BASE_URL = "https://statsapi.mlb.com/api/v1"  # Production URL

def get_teams(team_id=None, season=None, sport_id=None, division_id=None, game_type=None, league_ids=None,
            sport_ids=None, active_status=None, fields=None, hydrate=None):
    """
    Fetches and returns information about MLB teams.

    Args:
        team_id (int, optional): Unique Team Identifier.
        season (str, optional): Season of play.
        sport_id (int, optional): Top level organization of a sport.
        division_id (int, optional): Unique division identifier.
        game_type (str, optional): Type of game.
        league_ids (list, optional): List of Unique league identifiers.
        sport_ids (list, optional): List of sport identifiers.
        active_status (str, optional): Flag for fetching teams that are currently active (Y), inactive (N), pending (P), or all teams (B).
        fields (list, optional): List of specific fields to be returned.
        hydrate (str, optional): Parameter to include additional data.

    Returns:
        dict: A dictionary containing the teams data, or None if an error occurs.
    """
    url = "http://statsapi.mlb.com/api/v1/teams"
    if team_id:
        url = f"http://statsapi.mlb.com/api/v1/teams/{team_id}"
    params = {}

    if season:
        params['season'] = season
    if sport_id:
        params['sportId'] = sport_id
    if division_id:
        params['divisionId'] = division_id
    if game_type:
        params['gameType'] = game_type
    if league_ids:
        params['leagueIds'] = ','.join(map(str, league_ids))
    if sport_ids:
        params['sportIds'] = ','.join(map(str, sport_ids))
    if active_status:
        params['activeStatus'] = active_status
    if fields:
        params['fields'] = ','.join(fields)
    if hydrate:
        params['hydrate'] = hydrate

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching teams: {e}")
        return None

def get_all_players(sport_id=None,team_id=None,season=None):
    """Fetches and returns a list of all players for a given sport ID."""
    url = f"http://statsapi.mlb.com/api/v1/sports/{sport_id}/players"
    if team_id:
        url = f"http://statsapi.mlb.com/api/v1/sports/{sport_id}/players?teamID={team_id}"
    
    params = {}
    
    if season:
        params['season'] = season
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        players = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching players: {e}")
        return None
    return players


def get_team_roster(team_id, season=None):
    """
    Retrieves a team's roster, optionally for a specific season.

    Args:
        team_id (int): The unique identifier of the team.
        season (str, optional): The season for which to retrieve the roster. Defaults to None.

    Returns:
        dict: A dictionary containing the team's roster information, or None if an error occurs.
    """
    url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/roster"
    params = {}

    if season:
        params["season"] = season

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None



def get_basic_player_info(person_id):
    """
    Retrieves basic player information using the MLB Stats API.

    Args:
        person_id (int): The unique identifier for the player.

    Returns:
        dict: A dictionary containing basic player information, or None if an error occurs.
    """
    base_url = "https://statsapi.mlb.com/api/v1"
    person_url = f"{base_url}/people/{person_id}"
    try:
        person_response = requests.get(person_url)
        person_response.raise_for_status()  # Raise an exception for HTTP errors
        person_data = person_response.json()
        return person_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching basic player info: {e}")
        return None


def get_player_stats(person_id, stat_types=["season", "career"]):
    """
    Retrieves player stats using the MLB Stats API.

    Args:
        person_id (int): The unique identifier for the player.
        stat_types (list, optional): A list of stat types to retrieve. Defaults to ["season", "career"].

    Returns:
        dict: A dictionary containing player stats, or None if an error occurs.
    """
    base_url = "https://statsapi.mlb.com/api/v1"
    stats_url = f"{base_url}/people/{person_id}/stats"
    params = {"stats": stat_types}
    try:
        stats_response = requests.get(stats_url, params=params)
        stats_response.raise_for_status()
        stats_data = stats_response.json()
        return stats_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching player stats: {e}")
        return None


def get_player_headshot_from_url(person_id):
    """
    Retrieves a player's headshot image URL using a predefined URL pattern.

    Args:
        person_id (int): The unique identifier for the player.

    Returns:
        str or None: The URL of the player's headshot, or None if an error occurs.
    """
    base_url = "https://img.mlbstatic.com/mlb-photos/image/upload/w_213,d_people:generic::headshot:silo:current.png,q_auto:best,f_auto/v1/people"
    headshot_url = f"{base_url}/{person_id}/headshot/67/current"

    try:
        # Check if the image exists without downloading the whole thing
        response = requests.head(headshot_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        if response.status_code == 200:
            return headshot_url
        else:
            print(f"Image not found with status code {response.status_code}")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching player headshot: {e}")
        return None

def get_team_logo_url(team_id, theme = "light"):
    """
    Retrieves a team's logo URL based on the team ID and a theme ("light" or "dark").

    Args:
        team_id (int): The unique identifier for the team.
        theme (str): The theme for the logo ("light" or "dark").

    Returns:
        str or None: The URL of the team's logo, or None if an error occurs or the theme is invalid.
    """
    if theme not in ["light", "dark"]:
        print("Invalid theme. Please use 'light' or 'dark'.")
        return None
    
    base_url = "https://www.mlbstatic.com/team-logos"
    logo_url = f"{base_url}/{team_id}.svg"

    try:
        response = requests.head(logo_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        if response.status_code == 200:
            return logo_url
        else:
            print(f"Logo not found with status code {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching team logo: {e}")
        return None


def fetch_data(url, params=None):
    """Helper function to fetch data from the API."""
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def get_team_basic_details(team_id):
    """Fetches and displays team summary information."""

    # Team Information (including location):
    team_info_url = f"{BASE_URL}/teams/{team_id}"
    team_info = fetch_data(team_info_url)
    print(team_info)

    if team_info and 'teams' in team_info and isinstance(team_info['teams'], list) and len(team_info['teams']) > 0: #Check that the team_info is valid, there is a teams key, it is a list with at least one element
        team_name = team_info['teams'][0]['name']
        team_abbreviation = team_info['teams'][0]['abbreviation']
        team_location =  team_info['teams'][0]['venue']['name']

    # Coaches/Personnel:
    coaches_url = f"{BASE_URL}/teams/{team_id}/coaches"
    coaches_data = fetch_data(coaches_url)
    if coaches_data:
        if 'roster' in coaches_data:
            for entry in coaches_data['roster']:
                if entry.get('job') == "Manager":
                    #Check that the value of 'job' is exactly equal to "Manager"
                    manager =  entry.get('person')["fullName"]

    return team_name ,team_abbreviation,team_location,manager

def get_player_details_page_data(player_id):
    # Get and print basic player info
    basic_info = get_basic_player_info(player_id)
    if basic_info:
        print("Basic Player Information:")
        print(basic_info)

    # Get and print player stats
    player_stats = get_player_stats(player_id, stat_types=["season"])
    # Define the important metrics for MLB player's profile
    important_metrics = [
        "gamesPlayed", "avg", "obp", "slg", "ops", "homeRuns", "rbi", "hits", "strikeOuts", "baseOnBalls", "stolenBases"
    ]

    # Extract the relevant player info
    player_info = basic_info['people'][0]
    player_name = player_info['fullName']
    first_name = player_info['firstName']
    last_name = player_info['lastName']
    team_name = player_stats['stats'][0]['splits'][0]['team']['name']
    birth_date = player_info['birthDate']
    age = player_info['currentAge']
    position = player_info['primaryPosition']['name']
    height = player_info['height']
    weight = player_info['weight']
    mlb_debut = player_info['mlbDebutDate']

    # Extract the relevant stats
    stats = player_stats['stats'][0]['splits'][0]['stat']

    # Create a markdown text variable with basic info and important metrics
    markdown_text = f"### Player Profile: {player_name}\n"
    markdown_text += f"**Position:** {position} | **Team:** {team_name} | **Debut:** {mlb_debut}\n"
    markdown_text += f"**Birth Date:** {birth_date} | **Age:** {age} | **Height:** {height} | **Weight:** {weight} lbs\n\n"

    # Add important stats
    for metric in important_metrics:
        if metric in stats:
            markdown_text += f"- **{metric.replace('_', ' ').title()}:** {stats[metric]}\n"

    # Display the final markdown
    return markdown_text



#team_id_to_check = 147  # Example team ID, change to the desired ID, 147 is the NY Yankees [4, 5]
#get_team_summary(147)


"""
# Player Headshot from Static MLB url
headshot_url = get_player_headshot_from_url(player_id)
if headshot_url:
    print("Player Headshot URL:")
    print(headshot_url)
else:
    print("No player headshot found.")
    
team_id = 133
logo_url = get_team_logo_url(team_id,"light")

if logo_url:
    print("Team Logo URL:")
    print(logo_url)
else:
    print("No team logo found.")

# Example function call to list all teams in the 2025 season
season = "2025"
teams_data = get_teams(season=season,active_status="Y",sport_id=1)
print(teams_data)
if teams_data:
    print(f"Teams in the {season} season:")
    teams = teams_data.get('teams', [])
    for team in teams:
        print(f"- {team.get('name')} (ID: {team.get('id')})")
    print(len(teams))
else:
    print("Could not retrieve teams data.")
    
players_data = get_all_players(sport_id=1,season=season)
#print(players_data)
if players_data:
    print(f"Players in the {season} season:")
    players = players_data.get('people', [])
    for player in players:
        #pass
        print(f"- {player.get('fullName')} (ID: {player.get('id')}) (TeamID: {player.get('currentTeam', {}).get('id', 'N/A')})")
    print(len(players))
else:
    print("Could not retrieve players data.")
    

team_id = 114  # Example: Toronto Blue Jays
roster_data = get_team_roster(team_id, season)

if roster_data:
    print(f"Roster for team ID {team_id} in {season}:")
    for player_entry in roster_data.get('roster', []):
        player = player_entry.get('person', {})
        full_name = player.get('fullName', 'N/A')
        print(f"  - Player: {full_name}")
    print(len(roster_data.get('roster', [])))
else:
    print("Could not retrieve roster information.")
    
"""
