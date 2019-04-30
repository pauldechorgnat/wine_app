import pprint
from app.models import Cepage

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

            c = Cepage(
                id=id_,
                name=name,
                regions=regions,
                vignobles=vignobles,
                sous_regions=sous_regions,
                superficie_france=superficie_france,
                superficie_monde=superficie_monde,
                red=red
            )
            db.session.add(c)
            db.session.commit()

    except ValueError:
        continue


