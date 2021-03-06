from util import get_request, normalize


def get_outcome_name(type, home, away):
    if type == 'H':
        return home
    if type == 'A':
        return away
    if type == 'D':
        return 'draw'


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
            time = event['startTime'][:-1]
            id = f'{home} v {away} - {time}'
            events[id] = {}
            events[id]['home'] = home
            events[id]['away'] = away
            events[id]['time'] = time
            events[id]['sport'] = normalize(event['category']['name'])
            events[id]['region'] = normalize(event['class']['name'])
            events[id]['division'] = normalize(event['type']['name'])
            market = event['markets'][0]
            market_label = market['subType']
            events[id]['markets'] = {market_label: {}}

            for outcome in market['outcomes']:
                outcome_name = get_outcome_name(outcome['subType'], home, away)
                events[id]['markets'][market_label][outcome_name] = {
                    'odds': outcome['prices'][0]['decimal'],
                    'bookmaker': 'Toto'
                }

    print(f'Downloaded {len(events)} events from toto.')
