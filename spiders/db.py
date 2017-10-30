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
    data = list(map(lambda x: attr.asdict(x), proxies))
    result = collection.insert_many(data)
    return result.inserted_ids
