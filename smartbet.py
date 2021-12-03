import json
import os

from betcity import betcity
from toto import toto


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
