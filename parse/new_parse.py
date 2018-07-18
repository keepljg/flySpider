# _*_ coding: utf-8 _*_
from random import choice
import asyncio
import re
from lxml import etree
from abc import ABCMeta, abstractmethod
from urllib.parse import urljoin


from schedule.scheudle import Seed
from config import MAXTRY
from infoCrawler.asyncFetch import Fetcher

class BaseParser(object):
    __metaclass__ = ABCMeta
    level = None
    parseRule = ""
    item = None
    headers = None
    @classmethod
    async def parseResult(cls, engine, seed):
        if engine.proxies != None:
            try:
                proxy = choice(engine.proxies)
            except:
                engine.schedule_apkpure.InQueue(seed)
                asyncio.sleep(3) #休眠等待爬取proxy
                return
            await cls.deal_with_seed(engine, seed, proxy)
        else:
            await cls.deal_with_seed(engine, seed, None)

    @classmethod
    async def deal_with_seed(cls, engine, seed, proxy):
        data = await Fetcher.fetch(seed, engine.session, cls.headers, , data_type=seed.data_type, proxy=proxy)
        if data:
            urls = cls.extract_url(data)
            cls.parse_url(urls, engine, seed.level)
            if cls.item != None:
                this_item = cls.item(data)
                this_item.detail(engine.aiomysqler)

        else:
            try:
                engine.proxies.remove(proxy)
            except:
                pass
            seed.trytimes += 1
            if seed.trytimes < MAXTRY:
                engine.schedule_apkpure.InQueue(seed)


    @classmethod
    def parse_url(cls, urls, engine, level):
        if urls:
            for url in urls:
                if not url.startswith('http'):
                    url = urljoin(engine.base_url, url)
                if url not in engine.seen_urls:
                    engine.seen_urls.add(url)
                    engine.schedule_apkpure.q.put_nowait(Seed(url, 0, level + 1))


    @classmethod
    @abstractmethod
    def extract_url(cls, html):
        """必须实现的方法, 提取下一级的url"""
        pass


class ReParser(BaseParser):
    @classmethod
    def extract_url(cls, html):
        if cls.parseRule != '':
            urls = re.findall(cls.parseRule, html)
            return urls
        else:
            return None


class XPathParser(BaseParser):
    @classmethod
    def extract_url(cls, html):
        doc = etree.HTML(html)
        if cls.parseRule != '':
            urls = doc.xpath(cls.parseRule)
            return urls
        else:
            return None
