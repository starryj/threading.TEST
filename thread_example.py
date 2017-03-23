import threading
import queue
import requests
from bs4 import BeautifulSoup
import time
import random
TRUE = 1
my_lock = threading.Lock()
my_queue = queue.Queue()


class bt_fensi(threading.Thread):
    def __init__(self, q, lock):
        threading.Thread.__init__(self)
        self.q = q
        self.lock = lock


    def run(self):
        while TRUE:
            self.lock.acquire()
            if not self.q.empty():
                href = self.q.get()
                soup = Soup(href)
                span = soup.find('span',{'id': "file_text_span"})
                with open('bt.txt','a') as f:
                    f.write(str(span))
                print(f'{self.getName()}--{span.text}')
                self.lock.release()
            else:
                self.lock.release()
            time.sleep(1)


def Soup(url):
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"]
    user_agent = random.choice(user_agent_list)
    headers = {'User-Agent': user_agent,
               'Connection': 'keep-alive'}
    try:
        res = requests.get(url=url, headers=headers)
        res.encoding = 'utf-8'
        res.raise_for_status()
        html = res.text
        soup = BeautifulSoup(html, 'lxml')
        return soup
    except:
        print("网站没有回应!")


def get_link(url, q):
    soup = Soup(url)
    td = soup.find_all('td',{'class': 'torrentname'})
    for t in td:
        href = t.a['href']
        q.put('http://www.btfensi.com' + href)

t1 = time.time()
url = 'http://www.btfensi.com/'
my_list = []
for i in range(4):
    my_thread = bt_fensi(my_queue, my_lock)
    my_thread.start()
    my_list.append(my_thread)
my_lock.acquire()
get_link(url, my_queue)
my_lock.release()
while not my_queue.empty():
    pass
TRUE = 0
for t in my_list:
    t.join()
print("EENNDD")
print(time.time() - t1)