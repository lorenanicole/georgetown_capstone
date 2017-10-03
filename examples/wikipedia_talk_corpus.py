"""
Example script to locate a specific URL from website. In this case we could try to use the found URL to download the
zip file for the Wikipedia Detox corpus, but for brevity sake this shows a skeleton of how to use BeautifulSoup +
requests to outline such a process.
"""

import requests
from bs4 import BeautifulSoup


url = 'https://figshare.com/articles/Wikipedia_Talk_Corpus/4264973'

requests.get(url)

def soupify(url, parser='html.parser'):
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception('Unable to download data')

    return BeautifulSoup(response.content, parser)

soup = soupify(url)
items = soup.find('div', class_='items').find_all('a')
items = list(
    filter(lambda item: item.get('class') == ['download-button', 'simple-pink-button'], items)
)
items = list(map(lambda item: item.get('href'), items))

response = requests.get(items[0], allow_redirects=True)

if response.status_code != 200:
    print(str(response.reason) + ': ' + str(response.content))
    raise Exception('Unable to download data')


