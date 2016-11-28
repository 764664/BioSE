from collections import defaultdict
import logging
from src.models.schema import Term, SearchHistory
import inflect
p = inflect.engine()

common_words = ["a", "about", "after", "all", "an", "and", "any", "are", "as", "at", "be", "been", "before", "but", "by", "can", "could", "did", "do", "down", "first", "for", "from", "good", "great", "had", "has", "have", "he", "her", "him", "his", "I", "if", "in", "into", "is", "it", "its", "know", "like", "little", "made", "man", "may", "me", "men", "more", "Mr", "much", "must", "my", "no", "not", "now", "of", "on", "one", "only", "or", "other", "our", "out", "over", "said", "see", "she", "should", "so", "some", "such", "than", "that", "the", "their", "them", "then", "there", "these", "they", "this", "time", "to", "two", "up", "upon", "us", "very", "was", "we", "were", "what", "when", "which", "who", "will", "with", "would", "you", "your"]

def recommend_from_subscription(subscription):
    bag = defaultdict(int)
    papers = subscription.papers
        # voc = Vocabulary()
    for paper in papers:
        abstract = paper.abstract
        words = list(set([x.strip().strip(",.").lower() for x in abstract.split()]))
        for word in words:
            if word not in common_words:
                bag[word] += 1
    return bag

def recommend_from_user(user):
    bag = defaultdict(int)
    for subscription in user.subscriptions:
        all_tokens = []
        papers = subscription.papers
        num_paper = len(papers)
            # voc = Vocabulary()
        for paper in papers:
            try:
                abstract = paper.abstract
                words = list(set([x.strip().strip(",.").lower() for x in abstract.split()]))
                for word in words:
                    if word not in common_words:
                        bag[word] += 1
            except Exception as e:
                logging.warning(e)

        for paper in papers:
            # Map to terms
            abstract = paper.abstract

            tokens = ''.join(c for c in abstract if c.isalnum() or c.isspace()).split()
            tokens.extend([p.plural(token) for token in tokens])
            two_word = [ " ".join(tokens[i:i+2]) for i in range(len(tokens)-1)]
            two_word_plural = [ p.plural(w) for w in two_word ]
            tokens.extend(two_word)
            tokens.extend(two_word_plural)
            tokens.extend([t[0].upper()+t[1:] if t[0].islower() else t[0].lower()+t[1:] for t in tokens])
            all_tokens.extend(tokens)
        # print(Term.objects(name__in=all_tokens).count())
        all_tokens = set(all_tokens)
        try:
            all_tokens.remove('toes')
            all_tokens.remove('Toes')
        except:
            pass
        terms = [term.name for term in Term.objects(name__in=all_tokens)]

        for term in terms:
            bag[term] += num_paper

    for history in SearchHistory.objects(user=user.id):
        keyword = history.item.keyword
        bag[keyword] += 100

    return [(x, bag.__getitem__(x)) for x in sorted(bag, key=bag.__getitem__, reverse=True)]