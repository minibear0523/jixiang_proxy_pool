import asyncio
import uvloop
from crawler import Crawler
from db import insert_proxy

def crawl():
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    roots = [
        'http://ip181.com',
        'http://www.xicidaili.com/nn/',
        'http://www.xicidaili.com/wt/',
        'http://www.xicidaili.com/wn/',
        'http://www.kxdaili.com/dailiip/2/1.html',
        'http://www.kuaidaili.com/free/inha/1/',
        'http://www.xdaili.cn/ipagent/freeip/getFreeIps'
    ]
    crawler = Crawler(roots=roots, loop=loop, max_tasks=100)
    loop.run_until_complete(crawler.crawl())
    print('Finished {0} proxies in {1:.3f} secs'.format(len(crawler.done), crawler.t1-crawler.t0))

    result = insert_proxy(crawler.done)
    print('Insert {0} proxies, {1} success'.format(len(crawler.done), len(result)))

    crawler.close()
    loop.close()


if __name__ == '__main__':
    crawl()
