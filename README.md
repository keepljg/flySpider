# aioSpider
基于 asyncio,aiohttp,uvloop 的爬虫框架

# 运行环境
python3
# Usage


from engine.Engine import V1Engine
from item.item import Item
from selector.selector import Xpath
from parse.new_parse import BaseParser, XPathParser, ReParser

from config import *

if __name__ == '__main__':
    """urls 是初始urls数组"""
    urls = ['https://itunes.apple.com/cn/genre/ios/id36?mt=8']
    
    class urlItem(Item):
        title = Xpath("//h1/text()[2]")
        async def detail(self, aiomysql_heaper):
            sql = "insert into xxx (title) VALUES (%s)"
            params = (self.title,)
            # aiomysql_heaper.insert_into(sql, params)
            print("title is {}".format(self.title))
            
    #目前有xpath 和re 解析器 如有其它需求可以直接继承BaseParser 自己封装
    class parse1(XPathParser):
        level = 1
        parseRule = "//div[@class='grid3-column']//ul//li/a/@href"
        headers = normal

    class parse2(XPathParser):
        level = 2
        parseRule = "//div[@id='selectedcontent']//li/a/@href"
        headers = normal

    class parse3(BaseParser):
        level = 3
        headers = normal
        item = urlItem

    parses = [parse1, parse2, parse3]
    myEngine = V1Engine(urls, parses)
    myEngine.run()
    
# Seed
 url 种子 维护了url trytimes（重试次数） level（url深度）data_type（html 或者 图片）
 
# config
 """mysql 配置"""
HOST = ''
DATABASE = ''
PORT = 3306
USER = ''
PASSWORD = ''
CHARSET = 'utf8'

"""url queue 最大长度"""
URL_QUEUE_MAX_LENGTH = 0

"""url retry times"""

MAXTRY = 10

"""代理池最小值， 小于这个值重新爬取"""

MIN_PROXY_COUNT = 5

"""是否使用布隆过滤器"""

IS_USE_BLOOM = False

"""协程数"""

MAX_TASKS = 100

"""是否使用代理"""

IS_USE_PROXY = False

"""控制代理爬取时间"""

CRAWL_PROXY_TIME = 10

"""0 表示国内，1表示国外，用国外代理要保证服务器能翻墙"""

PROXY_TYPE = 1


"""用于验证代理有效性的网站"""

PROXY_VERIFICATION_URL = 'http://baidu.com'
#PROXY_VERIFICATION_URL = 'https://www.apple.com/shop/bag'
