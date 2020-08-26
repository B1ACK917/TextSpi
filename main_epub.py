from bs4 import BeautifulSoup
import requests
import os
from progressbar import *
import time
from fake_useragent import UserAgent
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
        self.output = None

    def get_proxy(self):
        return requests.get("http://127.0.0.1:5010/get/").json()

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

    def get_precontent(self, url):
        ua = UserAgent(verify_ssl=False)
        fake_header = {"User-Agent": ua.random}
        data = requests.get(url=url, headers=fake_header)
        html = data.text.encode(data.encoding).decode('utf-8').replace('\r', '')
        bs = BeautifulSoup(html, 'lxml')
        pre_content = bs.select('#content')
        return pre_content[0].get_text()[:-98].replace('    ', '\n\n    ')

    def get_content(self):
        pb = ProgressBar()
        for i in pb(range(self.catalog_nums)):
            url = self.catalog_url[i]
            while True:
                try:
                    pre_content = self.get_precontent(url)
                    break
                except Exception:
                    time.sleep(3)
            self.content.append(pre_content)

    def run(self):
        self.get_information()
        self.get_catalog()
        print('Book Name: {}\nAuthor: {}\nLast Update Time: {}'.format(self.name, self.author, self.current_time))
        self.get_content()
        self.output = self.name + '.txt'
        if not os.path.exists('output'):
            os.mkdir('output')
            os.mkdir(os.path.join('output', 'epub'))
        else:
            if not os.path.exists(os.path.join('output', 'epub')):
                os.mkdir(os.path.join('output', 'epub'))
        epub = epubmaker.EpubMaker()
        epub.set_arg(self.name, self.author, self.content, self.catalog, self.catalog_nums,
                     os.path.join('output', 'epub'))
        epub.run()


if __name__ == '__main__':
    url_list,book_list = [],[]
    print('Type your book url,x to stop')
    while True:
        kw = input()
        if kw == 'x':
            break
        url_list.append(kw.replace(' ', ''))
    for url in url_list:
        a = TextSpi(r'http://www.xbiquge.la', url)
        a.get_information()
        book_list.append(a.name)
        time.sleep(3)
    print('These are your wanted books: {}'.format(str(book_list)))
    print('Y/y to continue, N/n to quit')
    kw = input()
    if kw == 'Y' or kw == 'y':
        for item in url_list:
            a = TextSpi(r'http://www.xbiquge.la', item)
            a.run()
            time.sleep(5)
