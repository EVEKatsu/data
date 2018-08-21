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
                time.sleep(300)
        time.sleep(10)
    else:
        print('Pass: ' + url)


def get_players_information_by_esi(players, reload=False):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs', 'players.json')
    if os.path.isfile(path):
        with open(path, 'r') as file:
            all_players = json.load(file)
    else:
        all_players = {
            'character': {},
            'corporation': {},
            'alliance': {},
        }

    for player_type, player_ids in players.items():
        for player_id in player_ids:
            player_id = str(player_id)
            api_url = 'https://esi.evetech.net/latest/%ss/%s/' % (player_type, player_id)
            if reload or player_id not in all_players[player_type]:
                while True:
                    try:
                        with urllib.request.urlopen(api_url) as url:
                            json_dict = json.loads(url.read().decode())
                            value = OrderedDict()
                            for key in ['name', 'ticker']:
                                if key in json_dict:
                                    value[key] = json_dict[key]
                            all_players[player_type][player_id] = value
                        print('Download: ' + api_url)
                        break
                    except urllib.error.HTTPError:
                        print('urllib.error.HTTPError: ' + api_url)
                        time.sleep(300)
                time.sleep(10)
            else:
                print('Pass: ' + api_url)

    with open(path, 'w', encoding='utf-8') as file:
        json.dump(all_players, file, indent=4)

    result_players = {}
    for player_type, player_ids in players.items():
        result_players[player_type] = { str(player_id): all_players[player_type][str(player_id)] for player_id in player_ids }

    return result_players
