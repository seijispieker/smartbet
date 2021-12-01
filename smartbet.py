import json
import os

import requests
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
        'drilldownTagIds': 2, # Test with 11.
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
                    'odds' : outcome['prices'][0]['decimal'],
                    'bookmaker' : 'Toto'
                }

    print(f'Downloaded {len(events)} events from toto.')


def main():
    events = {}

    if not os.path.exists('output'):
        os.mkdir('output')

    toto(events)

    with open('output/smartbet.json', 'w') as f:
        json.dump(events, f)


if __name__ == '__main__':
    main()
