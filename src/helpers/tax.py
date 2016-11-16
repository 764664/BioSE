import csv
import logging

class Tax:
    def __init__(self):
        self.names = []
        with open('./resources/names.dmp') as f:
            reader = csv.reader(f, delimiter = "|")
            for line in reader:
                self.names.append(line[1].strip())

    def starts_with(self, keyword):
        r = [term for term in self.names if term.startswith(keyword)]
        r.sort(key=len)
        return r[:10]

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s')
    tax = Tax()
    logging.info(len(tax.names))
    logging.info(tax.starts_with("Homo sa"))
    logging.info(tax.starts_with("Ho"))