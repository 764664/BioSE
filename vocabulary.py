import redis
import logging
import sys
import goterm
import tax

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Vocabulary:
    def __init__(self):
        try:
            self.r = redis.StrictRedis(host='localhost', port=6379, db=0)
            self.redis_key = "biose"
            if not self.r.exists(self.redis_key):
                self.add_to_redis()
        except Exception:
            logger.error("Something went wrong with Redis.")
            sys.exit()

    def add_to_redis(self):
        self.goterm = goterm.GoTerm()
        self.tax = tax.Tax()
        for name in self.goterm.names:
            self.r.zadd(self.redis_key, 0, name)
        for name in self.tax.names:
            self.r.zadd(self.redis_key, 0, name)

    def exact_search(self, query):
        return (self.r.zrangebylex(self.redis_key, "[" + query, "[" + query))