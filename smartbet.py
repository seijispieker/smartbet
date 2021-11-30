import json
import os

import requests


def get_request(url, params=None, headers=None):
    response = requests.get(url, params=params, headers=headers)

    if response.status_code != requests.codes.ok:
        response.raise_for_status()

    return response


def main():
    events = {}

    if not os.path.exists('output'):
        os.mkdir('output')

    with open('output/smartbet.json', 'w') as f:
        json.dump(events, f)


if __name__ == '__main__':
    main()
