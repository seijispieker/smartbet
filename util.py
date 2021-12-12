from datetime import datetime, timedelta

import requests
import unidecode


def get_request(url, params=None, headers=None):
    response = requests.get(url, params=params, headers=headers)

    if response.status_code != requests.codes.ok:
        response.raise_for_status()

    return response


def normalize(string):
    return unidecode.unidecode(string.strip().lower())


def round_five_min(isoformat):
    time = datetime.fromisoformat(isoformat)
    seconds_round = timedelta(minutes=time.second//31)
    time = time.replace(hour=time.hour, minute=time.minute,
                        second=0) + seconds_round
    minutes_round = timedelta(minutes=((time.minute % 5)//3)*5)
    time = time.replace(hour=time.hour, minute=(time.minute//5)*5,
                        second=0) + minutes_round
    return time.isoformat()
