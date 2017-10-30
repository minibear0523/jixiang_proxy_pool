# encoding=utf-8
#
# proxy对象
#
import attr
import ujson
import arrow


@attr.s
class Proxy(object):
    """
    代理对象
    IP/Port; level: 代理类型; protocol(HTTP/HTTPS协议); location:地址;
    status: 验证状态; validated_time: 通过验证的次数; failed_time: 连续失败的次数
    created_time: 创建时间; last_modified_time: 上次修改时间; last_validated_time: 上次验证时间
    """
    IP = attr.ib()
    port = attr.ib()
    level = attr.ib()
    protocol = attr.ib()
    location = attr.ib()
    source = attr.ib()

    status = attr.ib(default=True)
    validated_time = attr.ib(default=0)
    failed_time = attr.ib(default=0)
    created_time = attr.ib(default=arrow.now().isoformat())
    last_modified_time = attr.ib(default=arrow.now().isoformat())
    last_validated_time = attr.ib(default=arrow.now().isoformat())
