from src.models.schema import Term
import logging
from IPython import embed

class GoTermParser:
    @staticmethod
    def parse():
        print("Start to import GO terms")

        count = 0
        name, definition, oid, namespace, tree_number_list, synonyms = None, None, None, None, [], []
        with open("resources/go.obo", 'r') as f:
            for line in f:
                if line == "[Term]\n" or line == "\n":
                    if oid and oid.find("GO") == 0:
                        term = Term(name=name, definition=definition, oid=oid, namespace=namespace, tree_number_list=tree_number_list, synonyms= synonyms, source="GO")
                        term.save()
                        count += 1
                        if count % 100 == 0:
                            print(".", end='',flush=True)
                    name, definition, oid, namespace, tree_number_list, synonyms = None, None, None, None, [], []
                else:
                    if line.find('name:') == 0:
                        name = line.strip()[6:]
                    if line.find('id:') == 0:
                        oid = line.strip()[4:]
                    elif line.find('def:') == 0:
                        definition = line.strip()[5:]
                    elif line.find('namespace:') == 0:
                        namespace = line.strip()[11:]
                    elif line.find('is_a:') == 0:
                        tree_number_list.append(line.strip()[6:16])
                    elif line.find('synonym:') == 0:
                        synonyms.append(line.strip()[11:])
        print("\nFinished importing GO terms")
        print("Start to fetch ancestor objects")
        count = 0
        for term in Term.objects(source="GO"):
            tree_number_list = term.tree_number_list
            for number in tree_number_list:
                try:
                    object = Term.objects(oid=number).get()
                    term.update(push__ancestors=object)
                except Exception as e:
                    logging.warning(e)
                    logging.warning(number)
            count += 1
            if count % 100 == 0:
                print(".", end='',flush=True)

    # def starts_with(self, keyword):
    #     len_keyword = len(keyword)
    #     r = [term for term in self.names if term[:len_keyword]==keyword]
    #     r.sort(key=len)
    #     return r[:10]

if __name__ == "__main__":
    GoTermParser.parse()
