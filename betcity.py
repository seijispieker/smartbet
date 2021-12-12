import concurrent.futures
import json
from pathlib import Path

from util import get_request, normalize


def download_group(group):
    url = f'https://eu-offering.kambicdn.org/offering/v2018/betcitynl/listView/{group["termKey"]}.json'
    params = {
        'lang': 'nl_NL',
        'market': 'NL'
    }
    response = get_request(url, params=params)
    return response.json()['events']


def get_outcome_name(outcome, home, away, localization):
    if 'participant' in outcome:
        name = normalize(outcome['participant'])

        if name in localization:
            name = localization[name]

        return name
    if outcome['label'] == '1':
        return home
    if outcome['label'] == '2':
        return away
    if outcome['label'] == 'X':
        return 'draw'


def betcity(events):
    print('Downloading events from betcity...')

    url = 'https://eu-offering.kambicdn.org/offering/v2018/betcitynl/group.json'
    params = {
        'lang': 'nl_NL',
        'market': 'NL'
    }
    response = get_request(url, params=params)
    groups = response.json()['group']['groups']
    betcity_events = []
    localize = {}

    data = Path('localization/betcity_localization.json').read_text()
    localization = json.loads(data)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(download_group, groups)

        for result in results:
            betcity_events += result

    match = 0

    for event in betcity_events:
        event_ = event['event']

        if 'COMPETITION' in event_['tags']:
            continue
        if len(event['betOffers']) == 0:
            continue

        home = normalize(event_['homeName'])
        away = normalize(event_['awayName'])

        if home in localization:
            home = localization[home]
        if away in localization:
            away = localization[away]

        time = event_['start']
        id = f'{home} v {away} - {time}'

        if id in events:
            for outcome in event['betOffers'][0]['outcomes']:
                if outcome['status'] == 'SUSPENDED':
                    continue

                outcome_name = get_outcome_name(outcome, home, away,
                                                localization)
                betcity_odds = outcome['odds'] / 1000

                if events[id]['markets']['MR'][outcome_name]['odds'] < betcity_odds:
                    events[id]['markets']['MR'][outcome_name] = {
                        'odds': betcity_odds,
                        'bookmaker': 'Betcity'
                    }

            match += 1
        else:
            events[id] = {}
            events[id]['sport'] = normalize(
                event_['path'][0]['englishName'])
            events[id]['markets'] = {'MR': {}}
            localize[home] = id
            localize[away] = id

            if len(event_['path']) == 2:
                events[id]['region'] = ''
                events[id]['division'] = normalize(
                    event_['path'][1]['englishName'])
            else:
                events[id]['region'] = normalize(
                    event_['path'][1]['englishName'])
                events[id]['division'] = normalize(
                    event_['path'][2]['englishName'])

            for outcome in event['betOffers'][0]['outcomes']:
                if outcome['status'] == 'SUSPENDED':
                    continue

                outcome_name = get_outcome_name(outcome, home, away,
                                                localization)
                events[id]['markets']['MR'][outcome_name] = {
                    'odds': outcome['odds'] / 1000,
                    'bookmaker': 'Betcity'
                }

    Path('output/localize_betcity.json').write_text(json.dumps(localize,
                                                               indent=4))
    total = len(betcity_events)
    print(
        f'Downloaded {total} events from betcity with {match} id\'s matched.')
