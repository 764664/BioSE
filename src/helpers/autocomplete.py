import logging

# import redis
# import src.helpers.goterm as goterm

# import src.helpers.tax as tax

# # import datetime

# logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)

# class InstantSearch:
#     def __init__(self, load_db = True):
#         # try:
#             self.r = redis.StrictRedis(host='localhost', port=6379, db=0)
#             self.redis_key = "biose"
#             if not self.r.exists(self.redis_key):
#                 self.add_to_redis()
#         # except Exception as e:
#         #     logger.error("Something went wrong with Redis.: {}".format(e))
#         #     sys.exit()

#     def add_to_redis(self):
#         self.goterm = goterm.GoTerm()
#         self.tax = tax.Tax()
#         for name in self.goterm.names:
#             self.r.zadd(self.redis_key, 0, name)
#         for name in self.tax.names:
#             self.r.zadd(self.redis_key, 0, name)

#     def search(self, s):
#         return(self.r.zrangebylex(self.redis_key, "["+s, "["+s+"z"))

#     def naive_search(self, s):
#         self.goterm = goterm.GoTerm()
#         self.tax = tax.Tax()
#         in_goterm = self.goterm.starts_with(s)
#         in_tax = self.tax.starts_with(s)
#         return in_goterm+in_tax

from src.models.schema import Term

class InstantSearch:
    @staticmethod
    def search(keyword):
        terms = Term.objects(name__istartswith=keyword).limit(20)
        return [term.serialize() for term in terms]

if __name__ == "__main__":
    instant = InstantSearch()
    # instant.add_to_redis()
    # logging.info(instant.search_in_redis("m"))
    # print(instant.naive_search("m"))
    # print(len(instant.tax.names))
    # print(instant.tax.names[100:120])
    # print(len(instant.goterm.names))
    # print(instant.goterm.names[100:120])
    # t = datetime.datetime.now().timestamp()
    # instant.search_in_redis("methylation")
    # print(datetime.datetime.now().timestamp() - t)
    # t = datetime.datetime.now().timestamp()
    # instant.naive_search("methylation")
    # print(datetime.datetime.now().timestamp() - t)