from src.models.schema import Paper, Term
# from src.helpers.vocabulary import Vocabulary
from flask import jsonify
import logging
import inflect
p = inflect.engine()
import re
from IPython import embed

class PaperController:
    @staticmethod
    def show(id):
        try:
            paper = Paper.objects(id=id).get()
            abstract = paper.abstract
            tokens = ''.join(c for c in abstract if c.isalnum() or c.isspace()).split()
            tokens.extend([p.plural(token) for token in tokens])
            two_word = [ " ".join(tokens[i:i+2]) for i in range(len(tokens)-1)]
            two_word_plural = [ p.plural(w) for w in two_word ]
            tokens.extend(two_word)
            tokens.extend(two_word_plural)
            tokens.extend([t[0].upper()+t[1:] if t[0].islower() else t[0].lower()+t[1:] for t in tokens])
            terms = [term.serialize() for term in Term.objects(name__in=tokens)]
            abstract = [abstract]
            for term in terms:
                # print('term {}; len {}'.format(term['name'], len(abstract)))
                name = term['name']
                for i in range(len(abstract)):
                    part = abstract[i]
                    if isinstance(part, str):
                        re1 = re.compile(name, re.I)
                        # print("search {} in {}".format(name, part))
                        m = re.search(re1, part)
                        if m:
                            term_here = term.copy()
                            term_here['here'] = m.group()
                            part = re.split(re1, part)
                            new_part = [term_here] * (len(part) * 2 - 1)
                            new_part[0::2] = part
                            part = new_part
                            abstract = abstract[:i] + part + abstract[i+1:]
                            continue
                        plural = p.plural(name)
                        re2 = re.compile(plural, re.I)
                        # print("search {} in {}".format(name, part))

                        m = re.search(re2, part)
                        if m:
                            term_here = term.copy()
                            term_here['here'] = m.group()
                            part = re.split(re2, part)
                            new_part = [term_here] * (len(part) * 2 - 1)
                            new_part[0::2] = part
                            part = new_part
                            abstract = abstract[:i] + part + abstract[i+1:]
            return jsonify(response=abstract)
        except Exception as e:
            logging.warning(e)
            return jsonify(response=list(), error=True)



