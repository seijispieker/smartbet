import json
from pathlib import Path

from arbitrage import arbitrage
from betcity import betcity
from toto import toto


def main():
    events = {}
    output = Path('output')

    if not output.exists():
        output.mkdir()

    toto(events)
    betcity(events)
    (output / Path('events.json')).write_text(json.dumps(events, indent=4))
    events = arbitrage(events)
    (output / Path('smartbet.json')).write_text(json.dumps(events))


if __name__ == '__main__':
    main()
