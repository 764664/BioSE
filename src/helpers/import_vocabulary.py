from src.models.schema import Term
import json
from IPython import embed

def serialize(term):
        # ancestors_all = []
        # ancestors = term.ancestors
        # while ancestors:
        #     ancestors_all.append([(ancestor.) for ancestor in ancestors
        return (
            {
                'name': term.name,
                'source': term.source,
                'definition': term.definition,
                'namespace': term.namespace,
                'id': str(term.id),
                'synonyms': term.synonyms,
                'ancestors': [serialize(ancestor) for ancestor in term.ancestors] if term.ancestors else None
            }
        )

print("Start to cache json for terms")
count = 0
for term in Term.objects:
    try:
        cached_json = json.dumps(serialize(term))
        term.update(set__cached_json=cached_json)
        count += 1
        if count % 100 == 0:
            print(".", end="", flush=True)
    except Exception as e:
        embed()
print("Finished caching json for terms")