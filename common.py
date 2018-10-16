import os
import time
import json
import urllib.error
import urllib.request
from collections import OrderedDict


def download_images(root_path, type_name, type_id, size, reload=False):
    EXTENSIONS = {
        'character': '.jpg',
        'corporation': '.png',
        'alliance': '.png',
    }

    filename = '%d_%d%s' % (type_id, size, EXTENSIONS[type_name])
    url = 'https://image.eveonline.com/%s/%s' % (type_name, filename)
    path = os.path.join(root_path, type_name, filename)

    if reload or not os.path.isfile(path):
        while True:
            try:
                data = urllib.request.urlopen(url).read()
                with open(path, mode="wb") as f:
                    f.write(data)
                print('Download: ' + url)
                break
            except urllib.error.HTTPError:
                print('urllib.error.HTTPError: ' + url)
                time.sleep(60)
        time.sleep(2)
    else:
        print('Pass: ' + url)


def get_players_information_by_esi(all_players, reload=False):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs', 'players_information.json')
    if os.path.isfile(path):
        with open(path, 'r') as file:
            cache_players = json.load(file)
    else:
        cache_players = {
            'character': {},
            'corporation': {},
            'alliance': {},
        }

    for player_key, players in all_players.items():
        for player_id in players.keys():
            player_id = str(player_id)
            api_url = 'https://esi.evetech.net/latest/%ss/%s/' % (player_key, player_id)
            if reload or player_id not in cache_players[player_key]:
                while True:
                    try:
                        with urllib.request.urlopen(api_url) as url:
                            json_dict = json.loads(url.read().decode())
                            value = OrderedDict()
                            for key in ['name', 'ticker']:
                                if key in json_dict:
                                    value[key] = json_dict[key]
                            cache_players[player_key][player_id] = value
                        print('Download: ' + api_url)
                        break
                    except urllib.error.HTTPError:
                        print('urllib.error.HTTPError: ' + api_url)
                        time.sleep(60)
                time.sleep(2)
            else:
                print('Pass: ' + api_url)

    with open(path, 'w', encoding='utf-8') as file:
        json.dump(cache_players, file, indent=4)

    players_information = OrderedDict()
    for player_key, players in all_players.items():
        players_information[player_key] = OrderedDict()
        for player_id, player in players.items():
            player_id = str(player_id)
            dict_ = cache_players[player_key][player_id].copy()
            for key, value in player.items():
                dict_[key] = value
            players_information[player_key][player_id] = dict_

    return players_information
