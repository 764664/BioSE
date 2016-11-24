from src.models.schema import Paper
from src.helpers.vocabulary import Vocabulary
from flask import jsonify
import logging

class PaperController:
    @staticmethod
    def show(id):
        try:
            paper = Paper.objects(id=id).get()
            abstract = paper.abstract
            tokens = ''.join(c for c in abstract if c.isalnum() or c.isspace()).split()
            result = []
            for token in tokens:
                v = Vocabulary()
                if v.exact_search(token):
                    result.append(token)
            return jsonify(response=list(set(result)))
        except Exception as e:
            logging.warning(e)
            return jsonify(response=list(), error=True)



