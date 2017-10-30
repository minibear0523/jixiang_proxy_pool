# encoding=utf-8
#
# 代理数据持久化保存
#
import ujson
import attr
from pymongo import MongoClient

client = MongoClient()
db = client.jixiang
collection = db.proxy


def insert_proxy(proxies):
    """
    Insert Proxy List From Crawler
    """
    result = collection.insert_many(proxies)
    return result.inserted_ids
