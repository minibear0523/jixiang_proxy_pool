# encoding=utf-8
import asyncio
from lxml import etree
import time
import urllib.parse
from asyncio import Queue
import aiohttp
import uvloop
import ujson, json
from pprint import pprint
import re


class Crawler(object):
    """
    """

    def __init__(self, root, loop=None, max_tasks=10, max_tries=5):
        self.loop = loop or asyncio.get_event_loop()
        self.root = root
        self.max_tasks = max_tasks
        self.max_tries = max_tries
        self.q = Queue(loop=self.loop)
        self.seen_urls = set()
        self.done = []
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.add_url(root)
        self.t0 = time.time()
        self.t1 = None
        self.root_domain = None
        parts = urllib.parse.urlparse(root)
        host, port = urllib.parse.splitport(parts.netloc)
        if not host:
            return
        else:
            self.root_domain = host

    def close(self):
        self.session.close()

    def add_url(self, url):
        print('%s add to queue' % url)
        self.seen_urls.add(url)
        self.q.put_nowait(url)

    async def crawl(self):
        workers = [asyncio.Task(self.work(), loop=self.loop) for _ in range(self.max_tasks)]
        self.t0 = time.time()
        # 抓取的实际操作, 所以在这里计算时间
        await self.q.join()
        self.t1 = time.time()
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
                response = await self.session.get(url, allow_redirects=False)
                break
            except aiohttp.ClientError as client_error:
                exception = client_error

            tries += 1
        else:
            return

        try:
            links = await self.parse_links(response)
            for link in links.difference(self.seen_urls):
                url = 'http://' + self.root_domain + link
                # self.q.put_nowait(url)
                self.add_url(url)
            self.seen_urls.update(links)
        finally:
            await response.release()

    async def parse_links(self, response):
        links = set()
        proxies = list()
        body = await response.read()

        if response.status == 200:
            content_type = response.headers.get('content-type')
            if content_type in ('text/html', 'application/xml'):
                text = await response.text()
                tree = etree.HTML(text)
                for proxy_info in tree.xpath('//tr')[1:]:
                    proxy_info = proxy_info.xpath('./td/text()')
                    ip = proxy_info[0].strip()
                    port = proxy_info[1].strip()
                    level = proxy_info[2].strip()
                    protocol = proxy_info[3].strip()
                    location = proxy_info[5].strip()

                    proxy = {
                        'ip': ip,
                        'port': port,
                        'level': level,
                        'protocol': protocol,
                        'location': location
                    }
                    self.record_statistic(proxy)

                for link in tree.xpath('//div[@class="page"]/a/@href'):
                    if not link.startswith('javascript'):
                        links.add(link)
        return links

    def record_statistic(self, statistic):
        self.done.append(statistic)

if __name__ == '__main__':
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    crawler = Crawler(root='http://ip181.com', loop=loop, max_tasks=100)
    loop.run_until_complete(crawler.crawl())
    print('Finished {0} proxies in {1:.3f} secs'.format(len(crawler.done), crawler.t1-crawler.t0))
    with open('results.json', 'w') as f:
        ujson.dump(crawler.done, f)
    crawler.close()
    loop.close()
