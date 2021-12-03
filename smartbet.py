import concurrent.futures
import json
import os

import requests
from requests.api import get
import unidecode


def get_request(url, params=None, headers=None):
    response = requests.get(url, params=params, headers=headers)

    if response.status_code != requests.codes.ok:
        response.raise_for_status()

    return response


def normalize(string):
    return unidecode.unidecode(string.strip().lower())


def toto(events):
    print('Downloading events from toto...')

    url = 'https://content.toto.nl/content-service/api/v1/q/time-band-event-list'
    params = {
        'drilldownTagIds': 2,  # Test with 11.
        'maxTotalItems': 100000000,
        'maxEventsPerCompetition': 100000000,
        'maxCompetitionsPerSportPerBand': 100000000,
        'maxEventsForNextToGo': 100000000,
        'includeChildMarkets': 'true',
        'marketSortsIncluded': 'MR'
    }

    response = get_request(url, params=params)

    for time_band_event in response.json()['data']['timeBandEvents']:
        for event in time_band_event['events']:
            home = normalize(event['teams'][0]['name'])
            away = normalize(event['teams'][1]['name'])
            time = event['startTime']
            id = f'{home} v {away} - {time}'
            events[id] = {}
            events[id]['home'] = home
            events[id]['away'] = away
            events[id]['sport'] = normalize(event['category']['name'])
            events[id]['region'] = normalize(event['class']['name'])
            events[id]['division'] = normalize(event['type']['name'])
            market = event['markets'][0]
            market_label = market['subType']
            events[id]['markets'] = {market_label: {}}

            for outcome in market['outcomes']:
                outcome_name = normalize(outcome['name'])
                events[id]['markets'][market_label][outcome_name] = {
                    'odds': outcome['prices'][0]['decimal'],
                    'bookmaker': 'Toto'
                }

    print(f'Downloaded {len(events)} events from toto.')


def get_outcome_name(outcome, home, away):
    if 'participant' in outcome:
        return normalize(outcome['participant'])
    if outcome['label'] == '1':
        return home
    if outcome['label'] == '2':
        return away
    if outcome['label'] == 'X':
        return 'draw'


def betcity(events):
    print('Downloading sports from betcity...')

    url = 'https://eu-offering.kambicdn.org/offering/v2018/betcitynl/group.json'
    params = {
        'lang': 'nl_NL',
        'market': 'NL'
    }

    response = get_request(url, params=params)
    id_match = 0
    total = 0

    for group in response.json()['group']['groups']:
        url = f'https://eu-offering.kambicdn.org/offering/v2018/betcitynl/listView/{group["termKey"]}.json'
        response = get_request(url, params=params)

        for event in response.json()['events']:
            event_ = event['event']

            if 'COMPETITION' in event_['tags']:
                continue
            if len(event['betOffers']) == 0:
                continue

            home = normalize(event_['homeName'])
            away = normalize(event_['awayName'])
            time = event_['start']
            id = f'{home} v {away} - {time}'

            if id in events:
                id_match += 1

                for outcome in event['betOffers'][0]['outcomes']:
                    if outcome['status'] == 'SUSPENDED':
                        continue

                    outcome_name = get_outcome_name(outcome, home, away)
                    betcity_odds = outcome['odds'] / 1000

                    if events[id]['markets']['MR'][outcome_name]['odds'] < betcity_odds:
                        events[id]['markets']['MR'][outcome_name] = {
                            'odds': betcity_odds,
                            'bookmaker': 'Betcity'
                        }
            else:
                events[id] = {}
                events[id]['sport'] = normalize(
                    event_['path'][0]['englishName'])
                events[id]['markets'] = {'MR': {}}

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

                    outcome_name = get_outcome_name(outcome, home, away)
                    events[id]['markets']['MR'][outcome_name] = {
                        'odds': outcome['odds'] / 1000,
                        'bookmaker': 'Betcity'
                    }

            total += 1

    print(
        f'Downloaded {total} events from betcity with {id_match} id\'s matched.')


def main():
    events = {}

    if not os.path.exists('output'):
        os.mkdir('output')

    toto(events)
    betcity(events)

    with open('output/smartbet.json', 'w') as f:
        json.dump(events, f)


if __name__ == '__main__':
    main()
