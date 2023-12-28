import requests
import urllib
from datetime import datetime
from config import PROPS_API_KEY as API_KEY
from data_utils import get_player_id, get_last_ten_games

BASE_URL = 'https://api.prop-odds.com'

def get_request(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()

    print('Request failed with status:', response.status_code)
    return {}

def get_nba_games():
    now = datetime.now()
    query_params = {
        'date': now.strftime('%Y-%m-%d'),
        'tz': 'America/New_York',
        'api_key': API_KEY,
    }
    params = urllib.parse.urlencode(query_params)
    url = BASE_URL + '/beta/games/nba?' + params
    return get_request(url)

def get_game_info(game_id):
    query_params = {
        'api_key': API_KEY,
    }
    params = urllib.parse.urlencode(query_params)
    url = BASE_URL + '/beta/game/' + game_id + '?' + params
    return get_request(url)


def get_markets(game_id):
    query_params = {
        'api_key': API_KEY,
    }
    params = urllib.parse.urlencode(query_params)
    url = BASE_URL + '/beta/markets/' + game_id + '?' + params
    return get_request(url)


def get_most_recent_odds(game_id, market):
    query_params = {
        'api_key': API_KEY,
    }
    params = urllib.parse.urlencode(query_params)
    # url = BASE_URL + '/beta/odds/' + game_id + '/' + market + '?' + params
    url = BASE_URL + '/v1/odds/' + game_id + '/' + market + '?' + params
    return get_request(url)

def compile_props(odds):
    props = {}
    # Probably don't want to go through all the sportsbooks
    for sportsbook in odds['sportsbooks']:
        for outcome in sportsbook['market']['outcomes']:
            player_name = outcome['participant_name']
            prop_line = outcome['handicap']
            props[player_name] = prop_line

    return props

def find_index(data, target):
    for key, value in data.items():
        if key == 'markets':
            for idx, market in enumerate(value):
                if market.get('name') == target:
                    return idx
            else:
                continue
    return -1

def main():
    games = get_nba_games()
    if len(games['games']) == 0:
        print('No games scheduled for today.')
        return

    combined_counts = {}  # Dictionary to hold combined counts for all players

    for game in games['games']:
        game_id = game['game_id']

        markets = get_markets(game_id)
        if len(markets['markets']) == 0:
            print('No markets found for a game.')
            continue
        
        target = "player_points_over_under"
        target_index = find_index(markets, target)

        if target_index == -1:
            print('No player points markets found for a game.')
            continue
        
        pts_market = markets['markets'][target_index]
        odds = get_most_recent_odds(game_id, pts_market['name'])

        props = compile_props(odds)

        for player_name in props:
            player_id = get_player_id(player_name)
            if player_id == -1:
                continue
            last_ten_games = get_last_ten_games(player_id)
            for index, row in last_ten_games.iterrows():
                if row['PTS'] >= props[player_name]:
                    combined_counts[player_name] = combined_counts.get(player_name, 0) + 1

    if not combined_counts:
        print('No data found for player points criteria in any game.')
        return

    # Sort the combined counts by the number of occurrences in descending order
    sorted_counts = dict(sorted(combined_counts.items(), key=lambda item: item[1], reverse=True))

    print("Player Counts (Last 10 games exceeding points prediction):")
    for player, count in sorted_counts.items():
        print(f'{player}: {count} games')

if __name__ == '__main__':
    main()
