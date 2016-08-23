import csv

fields = ["PMID", "Title", "Author", "Journal", "Year", "Abstract", "Journal_IF", 'Ranking']

class CSVHandler:
    @staticmethod
    def read_from_csv(filename):
        papers = []
        with open(filename, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                paper = row
                papers.append(paper)
        return papers

    @staticmethod
    def write_to_csv(filename, papers, additional_fields=[]):
        actual_fields = fields + additional_fields
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=actual_fields, extrasaction='ignore')
            writer.writeheader()
            for key, paper in papers.items():
                writer.writerow(paper)

    @staticmethod
    def write_list_to_csv(filename, papers, additional_fields=[]):
        actual_fields = fields + additional_fields
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=actual_fields, extrasaction='ignore')
            writer.writeheader()
            for paper in papers:
                writer.writerow(paper)