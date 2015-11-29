import requests
from lxml import html
import time

def get_h_index(name):
    s = requests.Session()
    user_agent = {'User-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:27.0) Gecko/20100101 Firefox/27.0',
                  }
    url = "https://scholar.google.com/citations?mauthors=" + name + "&hl=en&view_op=search_authors"
    r = s.get(url, headers = user_agent)
    tree = html.fromstring(r.content)
    url2 = "https://scholar.google.com" + tree.xpath('//h3[@class="gsc_1usr_name"]/a/@href')[0]
    url2 = url2.replace("&oe=ASCII", "")
    #url2 = "https://scholar.google.com/citations?user=glkyhpcAAAAJ"
    cookies = dict(NID='74=Hwu7YyNhq_kykZVHLr8Qqw0FCHW049o5WzdgfJmq_z_4UxJlSxKru9DBdC9XNqQ0rBEryyEsByf51g_yGOBTqm6uh4CBYmtnQtzRb17VQlP-fMQxYliLjFdaKe6Oq5AE')
    time.sleep(1)
    print(url2)
    r2 = requests.get(url2, headers = user_agent, cookies = cookies)
    tree2 = html.fromstring(r2.content)

    try:
        a = tree2.xpath('//td[@class="gsc_rsb_std"]/text()')
        citations = a[0]
        h = a[2]
        i10 = a[4]
        print(citations)
        print(h)
        print(i10)
    except IndexError:
        print(tree2.xpath("body//text()"))
        print(r2.request.headers)


get_h_index("Paul Horton")