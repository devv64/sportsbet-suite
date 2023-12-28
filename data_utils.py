from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
from nba_api.stats.library.parameters import Season
season = Season.default

def get_player_id(player_name):
    player_info = players.find_players_by_full_name(player_name)
    if len(player_info) == 0:
        print('No player found with name: ' + player_name)
        return -1
    return player_info[0]['id']

def get_last_ten_games(player_id, season=season):
    data = playergamelog.PlayerGameLog(player_id=player_id, season=season).get_data_frames()[0]
    return data.head(10)