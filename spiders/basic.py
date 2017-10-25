# encoding=utf-8
import requests
from lxml import etree
from selenium import webdriver
from items import Proxy


class BasicProxySpider(object):
    """
    基础代理爬虫, 包括抓取页面, 验证, 持久化
    """
    
