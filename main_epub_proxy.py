from bs4 import BeautifulSoup
import requests
import os
from progressbar import *
import time
import threading
import epubmaker


class TextSpi:
    def __init__(self, server, target):
        self.server = server
        self.target = target
        self.header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36',
        }
        self.name = 'Default'
        self.catalog = []
        self.author = 'Default'
        self.current_time = '0-0-0'
        self.introduction = 'Default'
        self.content = []
        self.catalog_url = []
        self.catalog_nums = 0
        self.url = requests.get(url=self.target)
        self.html = self.url.text.encode(self.url.encoding).decode('utf-8')
        self.bs = BeautifulSoup(self.html, 'lxml')
        self.max_threads = 75
        self.now_threads = 0
        self.output = None

    def get_proxy(self):
        while True:
            respond = requests.get("http://127.0.0.1:5010/get/").json()
            if respond.get("proxy") is not None:
                return respond
            else:
                time.sleep(5)

    def delete_proxy(self, proxy):
        requests.get("http://127.0.0.1:5010/delete/?proxy={}".format(proxy))

    def get_catalog(self):
        pre_catalog = self.bs.select('#list > dl > dd > a')
        for item in pre_catalog:
            self.catalog.append(item.get_text())
            self.catalog_url.append(self.server + item.get('href'))
        self.catalog_nums = len(self.catalog)

    def get_information(self):
        pre_name = self.bs.select('#info > h1')
        self.name = pre_name[0].get_text()
        pre_author = self.bs.select('#info > p:nth-child(2)')
        self.author = pre_author[0].get_text()[7:]
        pre_time = self.bs.select('#info > p:nth-child(4)')
        self.current_time = pre_time[0].get_text()[5:]
        pre_intro = self.bs.select('#intro > p:nth-child(2)')
        self.introduction = pre_intro[0].get_text()[5:]

    def get_precontent_with_proxy(self, url, index):
        proxy = self.get_proxy().get("proxy")
        retry_count = 5
        while True:
            try:
                data = requests.get(url=url, headers=self.header, proxies={"http": "http://{}".format(proxy)},
                                    timeout=3)
                html = data.text.encode(data.encoding).decode('utf-8').replace('\r', '')
                bs = BeautifulSoup(html, 'lxml')
                pre_content = bs.select('#content')
                self.content.append((str(pre_content[0])[:-183], index))
                break
            except Exception as e:
                retry_count -= 1
                if retry_count == 0:
                    # self.delete_proxy(proxy)
                    proxy = self.get_proxy().get("proxy")
                    retry_count = 5
                time.sleep(5)
        self.now_threads -= 1

    def get_precontent(self, url, index):
        while True:
            try:
                data = requests.get(url=url, headers=self.header, timeout=3)
                html = data.text.encode(data.encoding).decode('utf-8').replace('\r', '')
                bs = BeautifulSoup(html, 'lxml')
                pre_content = bs.select('#content')
                self.content.append((str(pre_content[0])[:-183], index))
                break
            except Exception as e:
                time.sleep(10)
        self.now_threads -= 1

    def get_content(self):
        for i in range(self.catalog_nums):
            while True:
                if self.now_threads < self.max_threads:
                    url = self.catalog_url[i]
                    threading.Thread(target=self.get_precontent_with_proxy, args=(url, i)).start()
                    self.now_threads += 1
                    break
                else:
                    time.sleep(3)
        while len(self.content) != self.catalog_nums:
            time.sleep(1)
        self.content = sorted(self.content, key=lambda x: x[1])

    def show_progress(self):
        while True:
            if len(self.content) < self.catalog_nums:
                print('\rDownloading... {}/{} has been downloaded.      '
                      'Threads Pool: {}/{}'.format(len(self.content), self.catalog_nums, self.now_threads,
                                                   self.max_threads),
                      end='',
                      flush=True)
                time.sleep(3)
            else:
                print('\rDownloading completed', flush=True)
                break

    def run(self):
        if self.name == 'Default':
            self.get_information()
        self.get_catalog()
        print('Book Name: {}\nAuthor: {}\nLast Update Time: {}'.format(self.name, self.author, self.current_time))
        threading.Thread(target=self.show_progress).start()
        self.get_content()
        self.output = self.name + '.txt'
        if not os.path.exists('output'):
            os.mkdir('output')
            os.mkdir(os.path.join('output', 'epub'))
        else:
            if not os.path.exists(os.path.join('output', 'epub')):
                os.mkdir(os.path.join('output', 'epub'))
        self.content = [i[0] for i in self.content]
        epub = epubmaker.EpubMaker()
        epub.set_arg(self.name, self.author, self.content, self.catalog, self.catalog_nums,
                     os.path.join('output', 'epub'))
        epub.run()


if __name__ == '__main__':
    url_list, book_list, spi_list = [], [], []
    pb = ProgressBar()
    print('Type your book url,x to stop')
    while True:
        kw = input()
        if kw == 'x':
            break
        url_list.append(kw.replace(' ', ''))
    for url in pb(url_list):
        a = TextSpi(r'http://www.xbiquge.la', url)
        a.get_information()
        book_list.append(a.name)
        spi_list.append(a)
        time.sleep(3)
    print('These are your wanted books: {}'.format(str(book_list)))
    print('Y/y to continue, N/n to quit')
    kw = input()
    if kw == 'Y' or kw == 'y':
        while spi_list:
            begin_time = time.perf_counter()
            spi_list[0].run()
            total_time = time.perf_counter() - begin_time
            print('{} has been downloaded. Total time: {} min,{} s'.format(spi_list[0].name, int(total_time // 60),
                                                                           int(total_time % 60)))
            spi_list.pop(0)
            time.sleep(3)
