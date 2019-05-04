import requests
from bs4 import BeautifulSoup
import re
import pprint
from app.models import AOC, Grape, User
from app import db

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
        vineyard=wine[1],
        still_white_wine=wine[2] != '',
        still_rose_wine=wine[3] != '',
        still_red_wine=wine[4] != '',
        sparkly_white_wine=wine[5] != '',
        sparkly_rose_wine=wine[6] != '',
        sparkly_red_wine=wine[7] != ''
    )
    db.session.add(aoc)

print(data[:3])

data = []
counter = 0
with open('static_data.tsv', 'r') as file:
    for line in file:
        if counter == 0:
            headers = line.split('\t')
            print(len(headers))
        else:
            print(len(line.split('\t')))
            data.append(dict(zip(headers, line.replace('\u202f', '').split('\t'))))
        counter += 1

pprint.pprint(data)

for wine in data:
    try:
        id_ = wine['id']
        if len(id_) > 0:
            id_ = int(id_)
            name = wine[u'Nom du cépage']
            regions = wine['Régions']
            sous_regions = wine['Sous-régions']
            superficie_france = wine['Superficie en France (ha)']
            superficie_monde = wine['Superficie mondiale (ha)']
            red = wine['Cépage'] == 'Noir'
            vignobles = wine['Vignobles']
            # changing types
            superficie_france = int(superficie_france) if len(superficie_france) > 0 else None
            superficie_monde = int(superficie_monde) if len(superficie_monde) > 0 else None

            c = Grape(
                id=id_,
                name=name,
                regions=regions,
                vineyards=vignobles,
                departments=sous_regions,
                area_fr=superficie_france,
                area_world=superficie_monde,
                red=red
            )
            db.session.add(c)

    except ValueError:
        continue


paul = User(username='paul', email='paul@paul.paul')
paul.set_password('paul')
db.session.add(paul)
db.session.commit()