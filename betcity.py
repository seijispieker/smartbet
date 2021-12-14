import concurrent.futures

from util import get_request, normalize, round_five_min


def download_group(group):
    url = f'https://eu-offering.kambicdn.org/offering/v2018/betcitynl/listView/{group["termKey"]}.json'
    params = {
        'lang': 'nl_NL',
        'market': 'NL'
    }
    response = get_request(url, params=params)
    return response.json()['events']


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
    print('Downloading events from betcity...')

    url = 'https://eu-offering.kambicdn.org/offering/v2018/betcitynl/group.json'
    params = {
        'lang': 'nl_NL',
        'market': 'NL'
    }
    response = get_request(url, params=params)
    groups = response.json()['group']['groups']
    betcity_events = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(download_group, groups)

        for result in results:
            betcity_events += result

    id_match = 0
    total = 0

    for event in betcity_events:
        event_ = event['event']

        if 'COMPETITION' in event_['tags']:
            continue
        if len(event['betOffers']) == 0:
            continue

        home = normalize(event_['homeName'])
        away = normalize(event_['awayName'])
        time = round_five_min(event_['start'][:-1])
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
            events[id]['home'] = home
            events[id]['away'] = away
            events[id]['time'] = time
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
