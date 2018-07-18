# _*_ coding: utf-8 _*_

from engine.Engine import V1Engine
from item.item import Item
from selector.selector import Xpath
from parse.new_parse import BaseParser, XPathParser, ReParser

from config import *

if __name__ == '__main__':

    urls = ['https://itunes.apple.com/cn/genre/ios/id36?mt=8']


    class urlItem(Item):
        title = Xpath("//h1/text()[2]")
        async def detail(self, aiomysql_heaper):
            sql = "insert into xxx (title) VALUES (%s)"
            params = (self.title,)
            # aiomysql_heaper.insert_into(sql, params)
            print("title is {}".format(self.title))

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



