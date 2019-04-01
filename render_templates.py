import os
import json
import csv
import datetime
from collections import OrderedDict

import jinja2

def get_json_by_file(path):
    if os.path.isfile(path):
        with open(path, 'r') as file:
            return json.load(file)
    return None

BASE_URL = 'https://evekatsu.github.io/data'
#BASE_URL = 'http://localhost:8000'

TYPES = get_json_by_file(os.path.join('.', 'docs', 'types.json'))

UNIVERSES = get_json_by_file(os.path.join('.', 'docs', 'universes.json'))

UNIVERSE_NAMES = {
    'eve': 'NewEden',
    'wormhole': 'Wormhole',
    'abyssal': 'Abyssal',
    'penalty': 'Penalty',
}

SETTINGS = get_json_by_file('settings.json')

LANGUAGES = OrderedDict(
    de='Deutsch',
    en='English',
    fr='le fran\u00e7ais',
    ja='日本語',
    ru='\u0440\u0443\u0441\u0441\u043a\u0438\u0439 \u044f\u0437\u044b\u043a',
    zh='\u4e2d\u6587',
)

DEFAULT_RENDER_KWARGS = {
    'SITENAME': 'Evekatsu',
    'SERVICE_NAME': 'Evekatsu',
    'SITEURL': BASE_URL,
    'STATIC_URL': BASE_URL + '/static',
    'DATETIME': datetime.datetime.now(),
    'VERSION': SETTINGS['version'],   
}

def url_tuple(name, url, attributes={}):
    attribute_text = ''
    for key, value in attributes.items():
        attribute_text += ' %s="%s"' % (key, value)
    return (name, url, attribute_text)

def generate_html(template_name, filename, kwargs={}):
    def is_tuple(value):
        return not isinstance(value, tuple)

    environment = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
    environment.tests['tuple'] = is_tuple
    template = environment.get_template(template_name)

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(template.render(**{**DEFAULT_RENDER_KWARGS, **kwargs}))

def generate_languages_table(filename, kwargs):
    kwargs['header'] = []
    if 'id_name' in kwargs:
        kwargs['header'].append(kwargs['id_name'])

    if 'sitename' in kwargs:
        kwargs['SITENAME'] = kwargs['sitename']
    elif 'title' in kwargs:
        kwargs['SITENAME'] = '%s | %s' % (kwargs['title'], DEFAULT_RENDER_KWARGS['SITENAME'])

    kwargs['items'] = sorted(kwargs['items'], key=lambda x: x[0])

    kwargs['header'].extend(LANGUAGES.values())
    generate_html('table.html', filename, kwargs)

def get_languages_item(item_dict, id_=None):
    item = []
    if id_:
        item.append(id_)

    for lang in LANGUAGES.keys():
        item.append(item_dict[lang])

    return item

def add_link_to_languages_item(languages_item, getter):
    item = []
    for name in languages_item:
        item.append(url_tuple(name, getter(languages_item)))

    return item

def generate_types():
    siteurl = BASE_URL + '/types'
    DEFAULT_RENDER_KWARGS['SITEURL'] = siteurl
    DEFAULT_RENDER_KWARGS['SERVICE_NAME'] = 'Evekatsu Types'

    base_path = os.path.join('.', 'docs', 'types')

    if not os.path.isdir(base_path):
        os.mkdir(base_path)

    for dir_name in ['groups', 'types']:
        dir_path = os.path.join(base_path, dir_name)
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)

    index_items = {
        'id_name': 'Category ID',
        'title': 'All Categories',
        'sitename': 'Evekatsu Types',
        'items': [],
        'links': [
            url_tuple('Download JSON', BASE_URL + '/types.json', {'download': 'types.json'}),
            url_tuple('Download CSV', BASE_URL + '/types.csv', {'download': 'types.csv'}),
            url_tuple('All Groups', siteurl + '/groups/'),
            url_tuple('All Types(Be careful because there is a lot)', siteurl + '/types/'),
        ],
    }
    categories = {}
    groups = {'index': {'id_name': 'Group ID', 'title': 'All Groups', 'items': []}}
    types = {'index': {'id_name': 'Type ID', 'title': 'All Types', 'items': []}}

    for type_id, type_ in TYPES['types'].items():
        group_id = type_['group_id']
        group = TYPES['groups'][str(group_id)]
        group_name = group['name']

        category_id = group['category_id']
        category = TYPES['categories'][str(category_id)]
        category_name = category['name']

        if category_name not in groups:
            index_items['items'].append(add_link_to_languages_item(
                get_languages_item(category, category_id),
                lambda x: siteurl + '/groups/%s.html' % x[2],
            ))

            groups[category_name] = {
                'id_name': 'Group ID',
                'title': 'Groups in %s' % category_name,
                'items': [],
                'links': [
                    url_tuple('Types in %s' % category_name, siteurl + '/types/%s.html' % category_name),
                ],
            }

        if group_name not in types:
            for name in ['index', category_name]:
                groups[name]['items'].append(add_link_to_languages_item(
                    get_languages_item(group, group_id),
                    lambda x: siteurl + '/types/%s.html' % x[2],
                ))

        for name in ['index', category_name, group_name]:
            if name not in types:
                types[name] = {
                    'id_name': 'Type ID',
                    'title': 'Types in %s' % name,
                    'items': [],
                }
            types[name]['items'].append(get_languages_item(type_, type_id))

    generate_languages_table(os.path.join(base_path, 'index.html'), index_items)

    for dir_name, dict_ in {'categories': categories, 'groups': groups, 'types': types}.items():
        for key, values in dict_.items():
            dir_path = os.path.join(base_path, dir_name, '%s.html' % key)
            generate_languages_table(dir_path, values)

    with open(os.path.join('.', 'docs', 'types.csv'), 'w') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerow(types['index']['header'])
        writer.writerows(types['index']['items'])

def generate_universes():
    siteurl = BASE_URL + '/universes'
    DEFAULT_RENDER_KWARGS['SITEURL'] = siteurl
    DEFAULT_RENDER_KWARGS['SERVICE_NAME'] = 'Evekatsu Universes'

    base_path = os.path.join('.', 'docs', 'universes')

    if not os.path.isdir(base_path):
        os.mkdir(base_path)

    for dir_name in ['regions', 'constellations', 'systems']:
        dir_path = os.path.join(base_path, dir_name)
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)

    regions = {'index': {'id_name': 'Region ID', 'title': 'All Regions', 'items': []}}
    constellations = {'index': {'id_name': 'Constellation ID', 'title': 'All Constellations', 'items': []}}
    systems = {'index': {'id_name': 'System ID', 'title': 'All Systems', 'items': []}}
    for system_id, system in UNIVERSES['systems'].items():
        constellation_id = system['constellation_id']
        constellation = UNIVERSES['constellations'][str(constellation_id)]
        constellation_name = constellation['name']

        region_id = constellation['region_id']
        region = UNIVERSES['regions'][str(region_id)]
        region_name = region['name']

        universe_id = region['universe_id']
        universe = UNIVERSES['universes'][str(universe_id)]
        universe_name = UNIVERSE_NAMES[universe['name']]

        if universe_name not in regions:
            regions[universe_name] = {
                'id_name': 'Region ID',
                'title': 'Regions in %s' % universe_name,
                'items': [],
                'links': [
                    url_tuple('Constellations in %s' % universe_name, siteurl + '/constellations/%s.html' % universe_name),
                    url_tuple('Systems in %s' % universe_name, siteurl + '/systems/%s.html' % universe_name),
                ],
            }

            constellations[universe_name] = {
                'id_name': 'Constellation ID',
                'title': 'Constellations in %s' % universe_name,
                'items': [],
                'links': [
                    url_tuple('Systems in %s' % universe_name, siteurl + '/systems/%s.html' % universe_name),
                ],
            }

            systems[universe_name] = {
                'id_name': 'System ID',
                'title': 'Systems in %s' % universe_name,
                'items': [],
            }

        if region_name not in constellations:
            for name in ['index', universe_name]:
                regions[name]['items'].append(add_link_to_languages_item(
                    get_languages_item(region, region_id),
                    lambda x: siteurl + '/constellations/%s.html' % x[2],
                ))

            constellations[region_name] = {
                'id_name': 'Constellation ID',
                'title': 'Constellations in %s' % region_name,
                'items': [],
                'links': [
                    url_tuple('Systems in %s' % region_name, siteurl + '/systems/%s.html' % region_name),
                ],
            }

        if constellation_name not in systems:
            for name in ['index', universe_name, region_name]:
                constellations[name]['items'].append(add_link_to_languages_item(
                    get_languages_item(constellation, constellation_id),
                    lambda x: siteurl + '/systems/%s.html' % x[2],
                ))

        for name in ['index', universe_name, region_name, constellation_name]:
            if name not in systems:
                systems[name] = {
                    'id_name': 'System ID',
                    'title': 'Systems in %s' % name,
                    'items': [],
                }
            systems[name]['items'].append(get_languages_item(system, system_id))

    universes = {
        'title': 'Universes',
        'sitename': 'Evekatsu Universes',
        'items': [],
        'links': [
            url_tuple('Download JSON', BASE_URL + '/universes.json', {'download': 'universes.json'}),
            url_tuple('Download CSV', BASE_URL + '/universes.csv', {'download': 'universes.csv'}),
            url_tuple('All Regions', siteurl + '/regions/'),
            url_tuple('All Constellations', siteurl + '/constellations/'),
            url_tuple('All Systems(Be careful because there is a lot)', siteurl + '/systems/'),
        ],
    }
    for universe_id, universe in UNIVERSES['universes'].items():
        languages_item = add_link_to_languages_item(
            get_languages_item(universe),
            lambda x: siteurl + '/regions/%s.html' % UNIVERSE_NAMES[x[1]],
        )
        universes['items'].append(languages_item)
    generate_languages_table(os.path.join(base_path, 'index.html'), universes)

    for dir_name, dict_ in {'regions': regions, 'constellations': constellations, 'systems': systems}.items():
        for key, values in dict_.items():
            dir_path = os.path.join(base_path, dir_name, '%s.html' % key)
            generate_languages_table(dir_path, values)

    with open(os.path.join('.', 'docs', 'universes.csv'), 'w') as file:
        writer = csv.writer(file, lineterminator='\n')
        writer.writerow(systems['index']['header'])
        writer.writerows(systems['index']['items'])

def main():
    generate_types()
    generate_universes()

if __name__ == '__main__':
    main()
