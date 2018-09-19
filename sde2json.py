import os
import json
import yaml
import zipfile
from collections import OrderedDict


DEBUG = os.getenv('EVEKATSU_DEBUG') in ['True', 'true', 'TRUE']

def get_sde_filename():
    for filename in os.listdir():
        base, ext = os.path.splitext(filename)
        if ext == '.zip' and 'sde-' in base and '-TRANQUILITY' in base:
            return filename
    return None

def generate_sde_json():
    # Only category IDs where the kill mail is issued.
    # include_category_ids = [
    #     6,  # Ship
    #     18, # Drone
    #     22, # Deployable
    #     23, # Starbase
    #     46, # Orbitals
    #     65, # Structure
    #     87, # Fighter
    # ]

    include_category_ids = [
        4,  # Material
        6,  # Ship
        7,  # Module
        8,  # Charge
        9,  # Blueprint
        16, # Skill
        18, # Drone
        20, # Implant
        22, # Deployable
        23, # Starbase
        25, # Asteroid
        30, # Apparel
        32, # Subsystem
        42, # Planetary Resources
        43, # Planetary Commodities
        46, # Orbitals
        65, # Structure
        66, # Structure Module
        87, # Fighter
        91, # Super Kerr-Induced Nanocoatings
    ]

    include_group_ids = []
    base_path = os.path.join('.', 'sde', 'fsd')

    sde = OrderedDict()
    sde['version'], ext = os.path.splitext(get_sde_filename())
    sde['category'] = {}    
    
    with open(os.path.join(base_path, 'categoryIDs.yaml')) as file:
        for i, items in yaml.load(file).items():
            if i not in include_category_ids:
                continue

            sde['category'][i] = {}
            sde['category'][i]['name'] = items['name']

    sde['group'] = {}
    with open(os.path.join(base_path, 'groupIDs.yaml')) as file:
        for i, items in yaml.load(file).items():
            if items['categoryID'] not in include_category_ids:
                continue

            include_group_ids.append(i)
            sde['group'][i] = {}
            sde['group'][i]['name'] = items['name']
            sde['group'][i]['category_id'] = items['categoryID']
                
    sde['type'] = {}
    with open(os.path.join(base_path, 'typeIDs.yaml')) as file:
        for i, items in yaml.load(file).items():
            if items['groupID'] not in include_group_ids:
                continue

            sde['type'][i] = {}
            sde['type'][i]['name'] = items['name']
            sde['type'][i]['group_id'] = items['groupID']

    with open(os.path.join('docs', 'sde.json'), 'w', encoding='utf-8') as file:
        json.dump(sde, file, indent=4)


def generate_universe_ids_json():
    def get_values(path, *names):
        values = {}
        with open(path) as file:
            target_yaml = yaml.load(file)
            for name in names:
                values[name] = target_yaml[name]
        return values

    region_dict = OrderedDict()
    constellation_dict = OrderedDict()
    solar_system_dict = OrderedDict()

    universe = OrderedDict()
    base_path = os.path.join('.', 'sde', 'fsd', 'universe')
    for universe_name in os.listdir(base_path):
        universe_path = os.path.join(base_path, universe_name)

        for region_name in os.listdir(universe_path):
            region_path = os.path.join(universe_path, region_name)

            if not os.path.isdir(region_path):
                continue

            region_values = get_values(
                os.path.join(region_path, 'region.staticdata'),
                'regionID'
            )
            region_id = str(region_values['regionID'])
            region_dict[region_id] = region_name

            for constellation_name in os.listdir(region_path):
                constellation_path = os.path.join(region_path, constellation_name)

                if not os.path.isdir(constellation_path):
                    continue

                constellation_values = get_values(
                    os.path.join(constellation_path, 'constellation.staticdata'),
                    'constellationID'             
                )
                constellation_id = str(constellation_values['constellationID'])
                constellation_dict[constellation_id] = OrderedDict(
                    name=constellation_name,
                    region_id=region_id,
                )

                for solar_system_name in os.listdir(constellation_path):
                    solar_system_path = os.path.join(constellation_path, solar_system_name)

                    if not os.path.isdir(solar_system_path):
                        continue

                    print(solar_system_path)

                    solar_system_values = get_values(
                        os.path.join(solar_system_path, 'solarsystem.staticdata'),
                        'solarSystemID',
                        'security'                 
                    )
                    solar_system_id = str(solar_system_values['solarSystemID'])
                    security = round(solar_system_values['security'], 1)
                    solar_system_dict[solar_system_id] = [
                        solar_system_name,
                        security,
                        region_id
                    ]

    with open(os.path.join('docs', 'universe_information.json'), 'w', encoding='utf-8') as file:
        json.dump(universe, file, indent=4)

def main():
    if not DEBUG or not os.path.isdir('sde'):
        with zipfile.ZipFile(get_sde_filename()) as zfile:
            zfile.extractall()

    generate_sde_json()
    #generate_universe_ids_json()

if __name__ == '__main__':
    main()