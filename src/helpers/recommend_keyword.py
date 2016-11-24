from collections import defaultdict
import logging

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
        papers = subscription.papers
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
    return [(x, bag.__getitem__(x)) for x in sorted(bag, key=bag.__getitem__, reverse=True)]