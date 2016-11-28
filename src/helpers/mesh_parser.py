import xml.etree.ElementTree as ET
from src.models.schema import Term
import logging

class MeshParser:
    @staticmethod
    def parse():
        print("Start to import MeSH terms")
        file = "resources/desc2017.xml"
        print("Start to read file")
        tree = ET.parse(file)
        print("Finished reading file")
        root = tree.getroot()
        count = 0
        for record in root.findall('DescriptorRecord'):
            count += 1
            if count % 100 == 0:
                print(".", end='',flush=True)
            try:
                oid = record.find('DescriptorUI').text
                name = record.find('DescriptorName').find('String').text
                try:
                    definition = list(record.iter('ScopeNote'))[0].text
                except:
                    definition = None
                try:
                    tree_number_list = [x.text for x in record.find('TreeNumberList')]
                except:
                    tree_number_list = None
                term = Term(oid=oid, name=name, definition=definition, tree_number_list=tree_number_list, source="MeSH")
                term.save()
            except Exception as e:
                logging.warning(e)
        print("Start to fetch ancestor objects")
        count = 0
        for term in Term.objects(source="MeSH"):
            tree_number_list = term.tree_number_list
            for number in tree_number_list:
                if '.' in number:
                    ancestor_oid = ".".join(number.split('.')[:-1])
                try:
                    object = Term.objects(oid=ancestor_oid).get()
                    term.update(push__ancestors=object)
                except Exception as e:
                    logging.warning(e)
                    logging.warning(number)
            count += 1
            if count % 100 == 0:
                print(".", end='',flush=True)
        print("\nFinished importing MeSH terms")

if __name__ == "__main__":
    MeshParser.parse()
