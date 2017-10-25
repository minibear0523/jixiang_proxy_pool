# encoding=utf-8


ATTRS = [
    'resource', 'ip', 'port', 'protocol', 'status', 'type', 'location', 'validated_time',
    'failed_time', 'last_modified_time'
]
class Proxy(object):
    """
    代理IP对象: resource, ip, port, status, type, location, protocol, validated_time, failed_time, last_modified_time
    """
    def __init__(self):
        self.data = {}

    def __getAttr__(key):
        if key not in ATTRS or key not in self.data:
            raise AttributeError
        return self.data[key]
