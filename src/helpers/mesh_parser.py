import xml.etree.ElementTree as ET
from src.models.schema import Term
import logging

class MeshParser:
    @staticmethod
    def parse():
        file = "resources/desc2017.xml"
        tree = ET.parse(file)
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
                    definition = record.iter('ScopeNote').text
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


if __name__ == "__main__":
    print("Start to import MeSH terms")
    MeshParser.parse()
    print("\nFinished importing MeSH terms")
