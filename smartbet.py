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

    data = Path('localization/localization.json').read_text()
    localization = json.loads(data)
    toto(events)
    betcity(events, localization)
    events = arbitrage(events)
    (output / Path('smartbet.json')).write_text(json.dumps(events))


if __name__ == '__main__':
    main()
