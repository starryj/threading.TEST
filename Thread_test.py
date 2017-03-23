import threading
import requests
import random
from bs4 import BeautifulSoup
import queue
import time
import csv


lock = threading.Lock()
href_qlock = threading.Lock()
bt_qlock = threading.RLock()
my_queue = queue.Queue()
href_q = queue.Queue()
bt_q = queue.Queue()
all_detail = []
movie_link = []
movie_name = []
magnet = []


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


class My_thread(threading.Thread):
    def __init__(self, q, q1, q2):
        threading.Thread.__init__(self)
        self.q = q
        self.q1 = q1
        self.q2 = q2

    def run(self):
        print("start:", self.getName())
        get_href(self.q, self.q1)
        get_bt(self.q1, self.q2)
        get_zimu(self.q2)
        print("end:", self.getName())


def get_link(start, end):
    lock.acquire()
    for n in range(start, end):
        if n == 1:
            url = 'http://subbt.com/mv'
            my_queue.put(url)
        else:
            url = 'http://subbt.com/mv?p=' + str(n)
            my_queue.put(url)
    lock.release()
    return my_queue


def get_href(q, hrefq):
    while True:
        lock.acquire()
        url = q.get()
        print(f'url:{url}')
        lock.release()
        soup = Soup(url)
        try:
            co = soup.find('div', {'class': 'col-md-10'}).find_all('div',
                                                                   {
                                                                       'class':
                                                                           "col-sm-3 col-md-3 col-xs-4 col-lg-2 nopl"})
            for c in co:
                h5 = c.find('h5')
                hre = h5.a['href']
                href = 'http://subbt.com' + hre  # 电影详细链接
                title = h5.a['title']  # 电影名称
                href_qlock.acquire()
                hrefq.put(href)
                href_qlock.release()
                movie_link.append(href)
                movie_name.append(title)

        except Exception as e:
            print(e)
        if q.empty():
            break


def get_bt(hreq, bq):
    while True:
        href_qlock.acquire()
        href = hreq.get()
        print(f'href:{href}')
        href_qlock.release()
        soup = Soup(href)
        detail = []
        co = soup.find('ul', {'class': 'detail'}).find_all('li')
        for c in co:
            di = c.div.text
            detail.append(di.strip())
        all_detail.append(detail)
        bt = soup.find('div', {'related allres'})
        data = bt.find_all('td', {'class': 'nobr'})
        bt_qlock.acquire()
        btl = []
        for d in data:
            bared = d.find('a')
            if bared:
                b_href = bared['href']
                bt_href = 'http://subbt.com' + b_href
                btl.append(bt_href)
        bq.put(btl)
        if hreq.empty():
            bt_qlock.release()
            break


def get_zimu(btq):
    while True:
        bt_qlock.acquire()
        hrefs = btq.get()
        print(f'zimu:{hrefs}')
        bt_qlock.release()
        magne = []
        for href in hrefs:
            soup = Soup(href)
            tdown = []
            h5 = soup.find('div', {'class': 'tdown'}).find_all('a')
            for h in h5:
                td = h['href']
                tdown.append(td)
            magne.append(tdown[1])
        magnet.append(magne)
        if btq.empty():
                break


t1 = time.time()
get_link(1,3)
th_list = []
for i in range(2):  # 设置线程数
    my_thread = My_thread(my_queue, href_q, bt_q)
    my_thread.start()
    th_list.append(my_thread)
for ii in th_list:
    ii.join()
t2 = time.time()
with open('movies.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['电影', '链接', '详情', '磁力链接', '字幕链接'])
for iii in range(len(movie_name)):
    print(movie_name[iii])
    csv_list = []
    for m in range(len(magnet[iii])):
        csv_list = [movie_name[iii], movie_link[iii], all_detail[iii], magnet[m]]
        with open('movies.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(csv_list)
        print(f'写入：{iii}.{m}')
print(f'总共用时：{t2 - t1}s')
