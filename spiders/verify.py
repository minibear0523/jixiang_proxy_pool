# encoding=utf-8
import requests
import ujson
import re
import time
import arrow
from pprint import pprint


Headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Upgrade-Insecure-Requests': '1'
}
IP_Reg = r'(\d+.\d+.\d+.\d+)'


class CheckIP(object):
    """
    IP分为三个阶段
    1. 检验匿名性: 先获取本地IP地址, 再使用代理获取IP地址, 查看是否改变
    2. 检验几个大型网站的可用性
    2.1 HTTP: sina.com.cn, sohu.com
    2.2 HTTPS: baidu, douban.com, tmall.com, jd.com
    3. 需要爬虫的几个网站: qichacha.com. qixin.com, tianyancha.com, gsxt.gov.cn
    """

    def __init__(self):
        self.local = ''
        self.http_check_url = 'http://ddns.oray.com/checkip'
        self.http_check_urls = [
            'http://ddns.oray.com/checkip',
            'http://www.sina.com.cn',
            'http://www.sohu.com'
        ]
        self.https_check_urls = [
            'https://ddns.oray.com/checkip',
            'https://www.tianyancha.com'
        ]
        self.spider_check_urls = [
            'http://www.qichacha.com',
            'http://www.qixin.com',
            'http://www.gsxt.gov.cn/index.html',
        ]
        self.session = requests.Session()
        self.session.headers.update(Headers)
        self.t0 = None
        self.t1 = None

    def close(self):
        self.session.close()

    def _get_local(self):
        """
        获取当前IP地址
        """
        req = self.session.get(self.http_check_url, headers=Headers)
        text = req.text()
        self.local = self.parse_ip(text)

    def parse_ip(self, html):
        return re.findall(IP_Reg, text)[0]

    def verify(self, proxy):
        """
        判断代理是否是HTTPS代理
        分别请求几个网站, 一旦发生错误就标记验证失败次数+1
        无论是不是高匿, HTTP代理请求HTTPS都无法达到匿名的效果
        优先使用高匿的HTTP/HTTPS代理, 目前只有天眼查是HTTPS服务器, 其他都是HTTP服务器
        """
        schema = proxy['protocol']
        if 'https' in schema:
            schema = 'https'
        else:
            schema = 'http'
        proxy_dict = {
            schema: '%s://%s:%s' % (schema, proxy['IP'], proxy['port'])
        }
        pprint(proxy_dict)

        try:
            response = self.session.get(self.http_check_url, proxies=proxy_dict, timeout=15)
        except Exception as error:
            print(error)
            return False
        if response.status_code != 200:
            return False

        for url in self.https_check_urls:
            try:
                print(url)
                response = self.session.get(url, proxies=proxy_dict, timeout=15)
            except Exception as error:
                if isinstance(error, requests.HTTPError):
                    return Fasle
            if response.status_code != 200:
                return False

        return True
