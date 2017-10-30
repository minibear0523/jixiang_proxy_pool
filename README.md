# 代理IP池框架
## 概述
用于集翔集团信息化部相关平台产品的微服务, 提供可用的代理IP地址, 包括免费代理和以后可能添加的付费代理.

## 运行环境
* Python 3.6+
* linux/macOS

## 运行依赖包
* uvloop
* aiohttp
* lxml
* selenium
* PhantomJS/ChromeDriver

## 源代码说明
整体采用asyncio+uvloop+aiohttp的方式异步抓取.

目前可以不借助Selenium的代理网站有:
* xicidaili.com
* ip181.com
* kuaidaili.com
* xdaili.cn

## TODO
1. [x] 设置解析规则, 加入到crawler.py中
2. [x] 学习设置asyncio的lock机制
3. [x] 设置IP代理验证
4. [x] 持久化保存IP代理
5. [x] 设置定时
6. [x] 接入search_visual, 提供API接口和可视化.
7. [x] 使用python-json-logger输出JSON格式化的log文件, 便于以后使用ElasticStack进行log监控.
