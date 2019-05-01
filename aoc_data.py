import requests
from bs4 import BeautifulSoup
import re

from app.models import AOC

url = 'https://fr.wikipedia.org/wiki/Vin_fran%C3%A7ais_b%C3%A9n%C3%A9ficiant_d%27une_AOC'

stop_words = {
    'sur',
    'sous',
    'le',
    'la',
    'les',
    'de',
    'du',
    'des',
    'ou'
}


def capitalize_wine_title(title, word='\\w+', stop_words_=stop_words):
    words = re.findall(pattern=word, string=title.lower())
    punctuations = re.subn(pattern=word, string=title, repl='')[0]
    result = ''
    for i in range(len(words)):
        if words[i] not in stop_words_:
            result += words[i].capitalize()
        else:
            result += words[i]
        if i != len(words) - 1:
            result += punctuations[i]
    return result


response = requests.get(url=url)
soup = BeautifulSoup(response.text, 'html.parser')
main_content = soup.find(id='mw-content-text')
table = main_content.find(name='table')

data = []
for row in table.find_all('tr'):
    cells = []
    for cell in row.find_all('td'):
        cell_content = cell.text.replace('\n', '')
        cell_content = capitalize_wine_title(cell_content)
        cells.append(cell_content.capitalize())
    data.append(cells)

headers = [
    'AOC_name',
    'vignobles',
    'vin_tranquille_blanc',
    'vin_tranquille_rose',
    'vin_tranquille_rouge',
    'vin_effervescent_blanc',
    'vin_effervescent_rose',
    'vin_effervescent_rouge'
]

data = data[2:]


for index, wine in enumerate(data):
    aoc = AOC(
        id=index + 1,
        name=wine[0],
        vignoble=wine[1],
        vin_tranquille_blanc=wine[2] != '',
        vin_tranquille_rose=wine[3] != '',
        vin_tranquille_rouge=wine[4] != '',
        vin_effervescent_blanc=wine[5] != '',
        vin_effervescent_rose=wine[6] != '',
        vin_effervescent_rouge=wine[7] != ''
    )
    db.session.add(aoc)
db.session.commit()


print(data[:3])