import requests
import gzip
import json
import concurrent.futures
import pandas as pd
from datetime import datetime


def get_latest_game_pk(team_id,season='2024'):
    """
    Retrieves the game_pk of the latest game for a given team ID using the MLB Stats API.

    Args:
        team_id (int): The unique identifier for the team.

    Returns:
        int: The game_pk of the latest game, or None if an error occurs.
    """
    url = f"https://statsapi.mlb.com/api/v1/schedule/?sportId=1&teamId={team_id}&season={season}&hydrate=team"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        
        # Extracted match information
        matches = []
        game_dates = []
        for date_info in data['dates']:
            for game in date_info['games']:
                match = {
                    'home_team': game['teams']['home']['team']['name'],
                    'away_team': game['teams']['away']['team']['name'],
                    'date': date_info['date'],
                    'game_in_series': game['gamesInSeries'],
                    'gamePk': game['gamePk']
                }
                game_dates.append(date_info['date'])
                matches.append(match)
                
        max_game_date = max(game_dates)
        print(max_game_date)
        for match in matches:
            if match['date'] == str(max_game_date):  
                return match
    
    except Exception as e:
        print(f"Request error: {e}")
        return None

def get_team_basic_details(team_id):
    """Fetches and displays team summary information."""
    BASE_URL = "https://statsapi.mlb.com/api/v1"
    # Team Information (including location):
    team_info_url = f"{BASE_URL}/teams/{team_id}"
    team_info = requests.get(team_info_url).json()
    print(team_info)

    if team_info and 'teams' in team_info and isinstance(team_info['teams'], list) and len(team_info['teams']) > 0: #Check that the team_info is valid, there is a teams key, it is a list with at least one element
        team_name = team_info['teams'][0]['name']
        team_abbreviation = team_info['teams'][0]['abbreviation']
        team_location =  team_info['teams'][0]['venue']['name']

    # Coaches/Personnel:
    
    coaches_url = f"{BASE_URL}/teams/{team_id}/coaches"
    response = requests.get(coaches_url)
    response.raise_for_status()
    coaches_data = response.json()
    if coaches_data:
        if 'roster' in coaches_data:
            for entry in coaches_data['roster']:
                if entry.get('job') == "Manager":
                    #Check that the value of 'job' is exactly equal to "Manager"
                    manager =  entry.get('person')["fullName"]

    return team_name ,team_abbreviation,team_location,manager


def get_last_game_for_team(team_id):
    """
    Retrieves the last game played by a specified team using the MLB Stats API
    using the /api/v1/teams/{teamId} endpoint.

    Args:
        team_id (int): The unique identifier for the team.

    Returns:
        dict or None: A dictionary containing the team data including the last game
                     if found, None otherwise.
    """
    url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}"
    params = {
        "gamesBack": '10',
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        if data:
            return data
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error during the request: {e}")
        return None



def get_last_game_id(person_id):
    """
    Retrieves the last game ID played by a player using the MLB Stats API.

    Args:
        person_id (int): The unique identifier for the player.

    Returns:
        int or None: The game ID of the last game played, or None if no games are found.
    """
    url = f"https://statsapi.mlb.com/api/v1/people/{person_id}/stats"
    params = {
        "stats": "gameLog",
        "hydrate": "game" # includes game data in response
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()

        if not data or 'stats' not in data or not data['stats']:
            print("No game data found for this player.")
            return None

        games = []
        games_info = {}

        for entry in data['stats'][0]['splits']:  # Accessing the 'splits' list inside 'stats'
            game_pk = entry['game']['gamePk']
            game_year = entry['season']
            game_date = entry['date']
            games_played = entry['stat']['gamesPlayed']
            
            games_info[game_pk] = {
                'year': game_year,
                'date': game_date,
                'games_played': games_played
            }
            
        
        last_game = None

        for entry in data['stats'][0]['splits']:
            game_date = entry['date']
            
            if last_game is None or datetime.strptime(game_date, "%Y-%m-%d") > datetime.strptime(last_game['date'], "%Y-%m-%d"):
                last_game = {
                    'gamePk': entry['game']['gamePk'],
                    'year': entry['season'],
                    'date': game_date,
                    'games_played': entry['stat']['gamesPlayed']
                }


        print(games_info,last_game)
        
        
        if not last_game:
            print("No game data found for this player.")
            return None
        return last_game['gamePk'],last_game['date']
    
        # Sort games by date
        #sorted_games = sorted(games,
        #                    key=lambda x: datetime.strptime(x['game']['gameDate'], '%Y-%m-%d'),
        #                    reverse=True)

        #if sorted_games:
        #    last_game = sorted_games
        #    return last_game['game']['gamePk']
        #else:
        #    print("No games found for this player.")
        #    return None


    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
        return None
    except (KeyError, ValueError) as e:
        print(f"Error processing API response: {e}")
        return None

def get_game_content(game_pk):
    """
    Retrieves game content, including highlights, for a particular game using the /api/v1/game/{game_pk}/content endpoint.
    has player_id
    has images of published articles
    """
    url = f"https://statsapi.mlb.com/api/v1/game/{game_pk}/content"
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()


def get_live_game_feed(game_pk, timecode=None):
    """
    Retrieves live game status, which may include commentary, using the /api/v1.1/game/{game_pk}/feed/live endpoint.
    """
    url = f"https://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live"
    params = {}
    if timecode:
        params['timecode'] = timecode
    headers = {'Accept-Encoding': 'gzip'}
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors
    #if response.headers.get('Content-Encoding') == 'gzip':
        #return gzip.decompress(response.content).decode('utf-8')
    #else:
    return response.json()


def get_game_timestamps(game_pk):
    """
    Retrieves live game status, which may include commentary, using the /api/v1.1/game/{game_pk}/feed/live endpoint.
    """
    url = f"https://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live/timestamps"
    params = {}
    
    headers = {'Accept-Encoding': 'gzip'}
    response = requests.get(url, params=params,stream=True,headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()

def get_game_play_by_play(game_pk, timecode=None, fields=None, inclusiveTimecode=None, accent=None):
    """
    Retrieves the play by play of a game, using the /api/v1/game/{game_pk}/playByPlay endpoint
    """
    url = f"https://statsapi.mlb.com/api/v1/game/{game_pk}/playByPlay"
    params = {}
    if timecode:
        params['timecode'] = timecode
    if fields:
        params['fields'] = fields
    if inclusiveTimecode:
        params['inclusiveTimecode'] = inclusiveTimecode
    if accent:
        params['accent'] = accent
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def get_schedule_with_highlights(date):
    """
    Retrieves the schedule for a given date with game highlights using the /api/v1/schedule endpoint with hydration
    """
    url = "https://statsapi.mlb.com/api/v1/schedule"
    params = {
        'date': date,
        'hydrate': 'game(content(highlights(all)))'
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def process_timestamp(game_pk,timestamp):
    """Fetch and process live game feed for a given timestamp."""
    time_feed = get_live_game_feed(game_pk, timecode=timestamp)
    current_play = time_feed['liveData']['plays']['currentPlay']
    
    result = current_play.get('result', {})
    about = current_play.get('about', {})
    count = current_play.get('count', {})
    matchup = current_play.get('matchup', {})
    
    # Basic game info
    play_event = result.get('event', None)
    play_description = result.get('description', None)
    away_score = result.get('awayScore', None)
    home_score = result.get('homeScore', None)
    is_out = result.get('isOut', None)
    
    inning = about.get('inning', None)
    half_inning = about.get('halfInning', None)
    is_top_inning = about.get('isTopInning', None)
    
    balls = count.get('balls', None)
    strikes = count.get('strikes', None)
    outs = count.get('outs', None)
    
    # Matchup details
    batter_id = matchup.get('batter', {}).get('id', None)
    batter_name = matchup.get('batter', {}).get('fullName', None)
    batter_side = matchup.get('batSide', {}).get('description', None)
    
    pitcher_id = matchup.get('pitcher', {}).get('id', None)
    pitcher_name = matchup.get('pitcher', {}).get('fullName', None)
    pitcher_hand = matchup.get('pitchHand', {}).get('description', None)
    
    # Pitch details (Extract last pitch info)
    play_events = current_play.get('playEvents', [])
    last_pitch = play_events[-1] if play_events else {}

    pitch_type = last_pitch.get('details', {}).get('type', {}).get('description', None)
    pitch_speed = last_pitch.get('pitchData', {}).get('startSpeed', None)
    pitch_call = last_pitch.get('details', {}).get('call', {}).get('description', None)
    pitch_code = last_pitch.get('details', {}).get('call', {}).get('code', None)
    play_id = last_pitch.get('playId', {})

    return {
        "timestamp": timestamp,
        "inning": inning,
        "half_inning": half_inning,
        "is_top_inning": is_top_inning,
        "play_event": play_event,
        "play_description": play_description,
        "away_score": away_score,
        "home_score": home_score,
        "is_out": is_out,
        "balls": balls,
        "strikes": strikes,
        "outs": outs,
        "batter_id": batter_id,
        "batter_name": batter_name,
        "batter_side": batter_side,
        "pitcher_id": pitcher_id,
        "pitcher_name": pitcher_name,
        "pitcher_hand": pitcher_hand,
        "pitch_type": pitch_type,
        "pitch_speed": pitch_speed,
        "pitch_call": pitch_call,
        "pitch_code": pitch_code,
        "play_id": play_id
    }


def get_game_stats(game_pk, stat_types=None, person_id=None, team_id=None, batter_id=None, pitcher_id=None, fields=None):
    """
    Retrieves game stats using the MLB Stats API.

    Args:
        game_pk (int): The unique primary key representing a game.
        stat_types (list, optional): A list of stat types to retrieve. Defaults to None.
        person_id (int, optional): A unique identifier for a player. Defaults to None.
        team_id (int, optional): A unique identifier for a team. Defaults to None.
        batter_id (int, optional): A unique identifier for a batter. Defaults to None.
        pitcher_id (int, optional): A unique identifier for a pitcher. Defaults to None.
        fields (list, optional) : A list of specific fields to be returned. Defaults to None.

    Returns:
        dict: A dictionary containing game stats, or None if an error occurs.
    """
    base_url = "https://statsapi.mlb.com/api/v1"
    params = {}

    if stat_types:
         params["stats"] = stat_types
    if fields:
        params["fields"] = fields
    
    if person_id:
         stats_url = f"{base_url}/people/{person_id}/stats/game/{game_pk}"
    elif team_id:
        stats_url = f"{base_url}/teams/{team_id}/stats"
        params["gamePk"] = game_pk
    elif batter_id and pitcher_id:
        stats_url = f"{base_url}/stats"
        params["gamePk"] = game_pk
        params["batterId"] = batter_id
        params["pitcherId"] = pitcher_id

    else:
        # if no player, team, batter or pitcher ids are specified, return general game stats
        stats_url = f"{base_url}/game/{game_pk}/boxscore"

    try:
        stats_response = requests.get(stats_url, params=params)
        stats_response.raise_for_status()
        stats_data = stats_response.json()
        return stats_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching game stats: {e}")
        return None


def extract_player_stats(data):
    stats = {}

    # Extract fielding stats
    fielding = next((split['stat'] for split in data.get('stats', [{}])[0].get('splits', []) if split.get('group') == 'fielding'), {})
    stats['assists'] = fielding.get('assists', 0)
    stats['putOuts'] = fielding.get('putOuts', 0)
    stats['errors'] = fielding.get('errors', 0)
    stats['chances'] = fielding.get('chances', 0)
    
    # Extract hitting stats
    hitting = next((split['stat'] for split in data.get('stats', [{}])[0].get('splits', []) if split.get('group') == 'hitting'), {})
    stats['gamesPlayed'] = hitting.get('gamesPlayed', 0)
    stats['hits'] = hitting.get('hits', 0)
    stats['runs'] = hitting.get('runs', 0)
    stats['strikeOuts'] = hitting.get('strikeOuts', 0)
    stats['atBats'] = hitting.get('atBats', 0)
    stats['rbi'] = hitting.get('rbi', 0)
    stats['totalBases'] = hitting.get('totalBases', 0)
    stats['plateAppearances'] = hitting.get('plateAppearances', 0)


    # Extract pitching stats
    pitching = next((split['stat'] for split in data.get('stats', [{}])[0].get('splits', []) if split.get('group') == 'pitching'), {})
    stats['gamesStarted'] = pitching.get('gamesStarted', 0)
    stats['caughtStealing'] = pitching.get('caughtStealing', 0)
    stats['stolenBases'] = pitching.get('stolenBases', 0)
    stats['stolenBasePercentage'] = pitching.get('stolenBasePercentage', '.---')
    stats['passedBall'] = pitching.get('passedBall', 0)
    stats['pickoffs'] = pitching.get('pickoffs', 0)
    
    
    # Extract pitch info, play IDs, and hit details
    play_details = []

    for stat_group in data.get('stats', []):
        # Loop through the splits in each stat group
        for play in stat_group.get('splits', []):
            # Debug print to see structure
            #print("Play Data:", play)
            
            # Check if play data exists
            play_info = play.get('stat', {}).get('play', {})
            
            # If play details are present, extract them
            if play_info:
                play_detail = {
                    'playId': play_info.get('playId', ''),
                    'description': play_info.get('details', {}).get('description', ''),
                    'isOut': play_info.get('isOut', False),
                    'type': play_info.get('details', {}).get('type', {}).get('description', ''),
                    'pitchDetails': {
                        'pitchType': play_info.get('pitchData', {}).get('type', {}).get('description', ''),
                        'pitchSpeed': play_info.get('pitchData', {}).get('startSpeed', 0),
                    },
                    'hitDetails': {
                        'launchSpeed': play_info.get('hitData', {}).get('launchSpeed', 0),
                        'trajectory': play_info.get('hitData', {}).get('trajectory', ''),
                        'totalDistance': play_info.get('hitData', {}).get('totalDistance', 0)
                    }
                }
                play_details.append(play_detail)

    stats['plays'] = play_details

    return stats


def get_highlights_for_team(team_id,match_id=None):
    ## Need Last game played by a team
    # Get game content (including highlights)
    if match_id is not None:
        game_pk = match_id
    else:
        game_details = get_latest_game_pk(team_id)
        game_pk = game_details['gamePk']
        
    team_name ,team_abbreviation,team_location,manager = get_team_basic_details(team_id)
    
    content = get_game_content(game_pk)
    recap = content.get('editorial', {}).get('recap', {}).get('mlb', {})

    #print(content['editorial']['recap']['mlb'])

    
    return {
        'team_name' : team_name,
        'team_abbreviation' : team_abbreviation,
        'team_location':team_location,
        'manager':manager,
        'home_team': game_details['home_team'],
        'away_team': game_details['away_team'],
        'game_in_series': game_details['game_in_series'],
        'headline': recap.get('headline', ''),
        'primary_image_url':   content['editorial']['recap']['mlb']['image']['cuts'][0]['src'],
        'body_content': recap.get('body', '')
    }


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