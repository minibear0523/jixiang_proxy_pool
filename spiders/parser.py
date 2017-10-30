# encoding=utf-8
#
# 尝试使用attrs这个包, 简单处理类声明, 这个类主要是用来保存不同网站的爬取规则
#
from lxml import etree
import ujson
from items import Proxy
from urllib.parse import urlparse
from pprint import pprint
import attr


class Parser(object):
    """
    提供一个classmethod来实现外部访问, 隐藏内部实现, crawler没必要知道parser调用哪个parse_接口
    """
    def __init__(self, url, html, more=False):
        self.url = url
        self.html = html
        self.more = more
        self.tree = etree.HTML(html)
        self.proxies = []
        self.links = set()

    def parse_proxy(self):
        print(self.url.host)
        if self.url.host == 'ip181.com':
            self.parse_ip181()
        elif self.url.host == 'www.xicidaili.com':
            self.parse_xici()
        elif self.url.host == 'www.kxdaili.com':
            self.parse_kaixin()
        elif self.url.host == 'www.kuaidaili.com':
            self.parse_kuai()
        elif self.url.host == 'www.xdaili.cn':
            self.parse_xdaili()
        return self.proxies, self.links

    def parse_ip181(self):
        """
        解析IP181.com的代理数据
        """
        assert self.url.host == 'ip181.com'

        for proxy_info in self.tree.xpath('//tr')[1:]:
            proxy_info = proxy_info.xpath('./td/text()')
            ip = proxy_info[0].strip()
            port = proxy_info[1].strip()
            level = proxy_info[2].strip()
            protocol = proxy_info[3].strip().lower()
            location = proxy_info[5].strip()

            self.proxies.append(attr.asdict(Proxy(IP=ip, port=port, level=level, protocol=protocol, location=location, source='ip181')))

        if self.more:
            for link in tree.xpath('//div[@class="page"]/a/@href'):
                if not link.startswith('javascript'):
                    url = '%s://%s%s' % (self.url.scheme, self.url.host, link)
                    self.links.add(url)

        pprint(self.proxies)
        pprint(self.links)

    def parse_xici(self):
        """
        解析西刺代理 www.xicidaili.com/nn/1
        """
        assert self.url.host == 'www.xicidaili.com'

        for proxy_info in self.tree.xpath('//table[@id="ip_list"]//tr')[1:]:
            proxy_info = proxy_info.xpath('./td')
            ip = proxy_info[1].xpath('./text()')[0].strip()
            port = proxy_info[2].xpath('./text()')[0].strip()
            location = ''.join(proxy_info[3].xpath('./a/text()')).strip()
            level = ''.join(proxy_info[4].xpath('./text()')).strip()
            protocol = ''.join(proxy_info[5].xpath('./text()')).strip().lower()
            print(ip, port, location, level, protocol)

            self.proxies.append(attr.asdict(Proxy(IP=ip, port=port, level=level, protocol=protocol, location=location, source='xicidaili')))

        if self.more:
            for link in tree.xpath('//div[@class="pagination"]/a/@href'):
                url = '%s://%s%s' % (self.url.scheme, self.url.host, link)
                self.links.add(url)

    def parse_kaixin(self):
        """
        解析开心代理 www.kxdaili.com/dailiip/2/1.html#ip
        """
        assert self.url.host == 'www.kxdaili.com'

        for proxy_info in self.tree.xpath('//table[@class="ui table segment"]/tbody/tr'):
            proxy_info = proxy_info.xpath('./td/text()')
            ip = proxy_info[0].strip()
            port = proxy_info[1].strip()
            level = proxy_info[2].strip()
            protocol = proxy_info[3].strip().lower()
            location = proxy_info[5].strip()

            self.proxies.append(attr.asdict(Proxy(IP=ip, port=port, level=level, protocol=protocol, location=location, source='kxdaili')))

        if self.more:
            for link in self.tree.xpath('//div[@class="page"]/a/@href'):
                url = '%s://%s%s' % (self.url.scheme, self.url.host, link)
                self.links.add(url)


    def parse_kuai(self):
        """
        解析快代理 www.kuaidaili.com/free/inha/1/
        """
        assert self.url.host == 'www.kuaidaili.com'

        for proxy_info in self.tree.xpath('//table[@class="table table-bordered table-striped"]/tbody/tr'):
            proxy_info = proxy_info.xpath('./td/text()')
            ip = proxy_info[0].strip()
            port = proxy_info[1].strip()
            level = proxy_info[2].strip()
            protocol = proxy_info[3].strip().lower()
            location = proxy_info[4].strip()

            self.proxies.append(attr.asdict(Proxy(IP=ip, port=port, level=level, protocol=protocol, location=location, source='kuaidaili')))

        if self.more:
            for link in self.tree.xpath('//div[@id="listnav"]/ul/li/a/@href'):
                url = '%s://%s%s' % (self.url.scheme, self.url.host, link)
                self.links.add(url)

    def parse_xdaili(self):
        """
        解析讯代理 www.xdaili.cn/freeproxy
        """
        assert self.url.host == 'www.xdaili.cn'
        result = ujson.loads(self.html)

        for proxy_info in result['RESULT']['rows']:
            ip = proxy_info['ip']
            port = proxy_info['port']
            level = proxy_info['anony']
            protocol = proxy_info['type'].lower()
            location = proxy_info['position']

            self.proxies.append(attr.asdict(Proxy(IP=ip, port=port, level=level, protocol=protocol, location=location, source='xdaili')))
