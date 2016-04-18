import goterm
import tax
import logging
import string
import db

class InstantSearch:
    def __init__(self, load_db = True):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s')
        logging.info("Initiating instant search.")
        self.goterm = goterm.GoTerm()
        self.tax = tax.Tax()
        self.cache = {}
        if load_db:
            self.load_db()
        logging.info("Finished initiation of instant search.")

    def search(self, string):
        if string in self.cache:
            return [x[0] for x in self.cache[string]]
        in_goterm = self.goterm.starts_with(string)
        in_tax = self.tax.starts_with(string)
        result = in_goterm + in_tax
        self.cache[string] = [[x, 1] for x in result]
        return result

    def load_db(self):
        db.database.connect()
        for a in string.ascii_lowercase:
            self.cache[a] = list(map(lambda x:[x, 1], db.InstantSearch.get(keyword=a).result.split(",")))
            for b in string.ascii_lowercase:
                self.cache[a+b] = list(map(lambda x:[x, 1], db.InstantSearch.get(keyword=a+b).result.split(",")))
        db.database.close()

if __name__ == "__main__":
    instant = InstantSearch()
    logging.info(instant.search("m"))