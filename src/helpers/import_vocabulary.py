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
                'oid': term.oid,
                'ancestors': [serialize(ancestor) for ancestor in term.ancestors] if term.ancestors else None
            }
        )

print("Start to cache json for terms")
count = 0
for term in Term.objects.no_cache():
    try:
        h = serialize(term)
        cached_json = json.dumps(h)
        term.update(set__cached_json=cached_json)
        count += 1
        # if count % 100 == 0:
        #     print(".", end="", flush=True)
        print("{}: {}".format(count, len(cached_json)))
    except Exception as e:
        embed()
print("Finished caching json for terms")