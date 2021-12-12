import requests
import unidecode


def get_request(url, params=None, headers=None):
    response = requests.get(url, params=params, headers=headers)

    if response.status_code != requests.codes.ok:
        response.raise_for_status()

    return response


def normalize(string):
    return unidecode.unidecode(string.strip().lower())
