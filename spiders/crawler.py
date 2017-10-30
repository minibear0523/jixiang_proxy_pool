# encoding=utf-8
#
# 通过python3.6上源生的asyncio和uvloop以及aiohttp扩展, 实现异步网络请求.
# 使用aiohttp而不是requests的原因是requests是同步阻塞请求, aiohttp是异步的.
# uvloop的速度要比asyncio自带的get_event_loop处理速度更快, 而且配置简单, 不需要修改代码
# ujson操作json文件的原因也是因为ujson是python中处理json速度最快的插件.
#
import asyncio
from lxml import etree
import time
import urllib.parse
from asyncio import Queue
import aiohttp
import uvloop
import ujson
import re
import cgi
from parser import Parser
from pprint import pprint

Headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Upgrade-Insecure-Requests': '1'
}


class Crawler(object):
    """
    使用asyncio+uvloop+aiohttp实现异步抓取数据的需求
    """

    def __init__(self, roots, loop=None, max_tasks=10, max_tries=5):
        self.loop = loop or asyncio.get_event_loop()
        self.roots = roots
        self.max_tasks = max_tasks
        self.max_tries = max_tries
        self.q = Queue(loop=self.loop)
        self.seen_urls = set()
        self.done = []
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.t0 = time.time()
        self.t1 = None
        self.root_domains = []
        for root in roots:
            self.add_url(root)
            parts = urllib.parse.urlparse(root)
            host, port = urllib.parse.splitport(parts.netloc)
            if not host:
                return
            else:
                self.root_domains.append(host)

    def close(self):
        self.session.close()

    def add_url(self, url):
        """
        add_url不判断是否在seen_urls中, 需要在调用add_url之前进行判断
        """
        print(url)
        self.seen_urls.add(url)
        self.q.put_nowait(url)

    async def crawl(self):
        workers = [asyncio.Task(self.work(), loop=self.loop) for _ in range(self.max_tasks)]
        self.t0 = time.time()
        # 抓取的实际操作, 所以在这里计算时间
        await self.q.join()
        self.t1 = time.time()
        # 当请求完成之后要cancel掉worker, 不然会一直阻塞.
        for w in workers:
            w.cancel()

    async def work(self):
        try:
            while True:
                url = await self.q.get()
                assert url in self.seen_urls
                await self.fetch(url)
                self.q.task_done()
        except asyncio.CancelledError:
            pass

    async def fetch(self, url):
        tries = 0
        exception = None
        while tries < self.max_tries:
            try:
                response = await self.session.get(url, headers=Headers, allow_redirects=False)
                break
            except aiohttp.ClientError as client_error:
                exception = client_error
                print(exception)
            tries += 1
        else:
            return

        try:
            links = await self.parse_links(response)
            for link in links.difference(self.seen_urls):
                self.add_url(link)
            self.seen_urls.update(links)
        finally:
            await response.release()

    async def parse_links(self, response):
        links = set()
        proxies = list()
        body = await response.read()

        if response.status == 200:
            content_type = response.headers.get('content-type')
            if content_type:
                content_type, _ = cgi.parse_header(content_type)

            if content_type in ('text/html', 'application/xml'):
                text = await response.text()
                proxies, links = Parser(url=response.url, html=text, more=False).parse_proxy()
                self.record_statistic(proxies)
        else:
            print('request failed: %s', response.status)
        return links

    def record_statistic(self, proxies):
        self.done.extend(proxies)
