from bs4 import BeautifulSoup

from util import get_request, normalize


def generate_urls():
    base_url = 'https://www.bingoal.nl'
    response = get_request(f'{base_url}/nl/Sport')
    soup = BeautifulSoup(response.content, 'html.parser')
    urls = []

    for sport in soup.find('ul', 'tree').find_all('li', recursive=False):
        sport_name = normalize(sport.a.strong.text)
        for region in sport.ul.find_all('li', recursive=False):
            for division in region.ul.find_all('li', recursive=False):
                url_entry = {
                    'sport': normalize(sport.a.strong.text),
                    'region': normalize(region.a.text),
                    'division': normalize(division.a.text),
                    'url': f'{base_url}{division.a["href"]}'
                }
                urls.append(url_entry)

    return urls


def bingoal(events):
    print('Downloading events from bingoal...')
    urls = generate_urls()
