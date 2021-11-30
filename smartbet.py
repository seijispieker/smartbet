import json
import os


def main():
    events = {}

    if not os.path.exists('output'):
        os.mkdir('output')

    with open('output/smartbet.json', 'w') as f:
        json.dump(events, f)


if __name__ == '__main__':
    main()