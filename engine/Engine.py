# _*_ coding: utf-8 _*_

from threading import Thread

import socket
import asyncio
import aiohttp
from asyncio import Lock
from datetime import datetime
import re
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


from proxyCrawler.CrawlProxy import asyncCrawlProxy
from schedule.scheudle import Seed
from config import MAX_TASKS, get_logger, MIN_PROXY_COUNT
from schedule.scheudle import Schedule
from mysqlHeaper.AioMysqlHeaper import MysqlHeaper
logger = get_logger(__name__)

class V1Engine:
    def __init__(self, urls, parser, loop=None):
        self.urls = urls
        """调度器 维护一个async queue"""
        self.schedule_apkpure = Schedule(loop)
        self.loop = loop or asyncio.get_event_loop()
        self.max_tasks = MAX_TASKS
        self.conn = aiohttp.TCPConnector(family=socket.AF_INET,
                                         verify_ssl=False,
                                         use_dns_cache=True)
        self.seen_urls = set()
        self.session = aiohttp.ClientSession(loop=self.loop, connector=self.conn)
        self.aiomysqler = MysqlHeaper()
        self.crawlProxy = asyncCrawlProxy(self.loop)
        self.lock = Lock()
        self.proxies = []
        self.parsers = parser
        self.base_url = ""

    async def crawler(self):
        """create async mysql pool"""
        await self.aiomysqler.get_pool(self.loop)

        self.put_initial_seeds()
        self.proxies = await self.crawlProxy.run(self.session)
        """create max_tasks coroutine"""
        workers = [asyncio.Task(self.worker(), loop=self.loop)
                   for _ in range(self.max_tasks)]

        """block until all items in the queue have been gotten and processed"""
        await self.schedule_apkpure.q.join()

        for w in workers:
            w.cancel()

    def run(self):
        logger.info('Spider started!')
        start_time = datetime.now()
        if self.base_url == '':
            self.base_url = re.match(r"((http|https)://.*?).*", self.urls[0]).group(1)

        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self.crawler())
        except KeyboardInterrupt:
            for task in asyncio.Task.all_tasks():
                task.cancel()
            loop.run_forever()
        finally:
            end_time = datetime.now()
            logger.info('Time usage: {}'.format(end_time - start_time))

    def put_initial_seeds(self):
        for url in self.urls:
            if url not in self.seen_urls:
                self.schedule_apkpure.q.put_nowait(Seed(url, 0, 1))
                self.seen_urls.add(url)

    async def worker(self):
        """
        :param seens_urls: input seens_url(url, retrytimes)
        :param aiomysqler:
        :return: new input seens_url and get item to mysql
        """
        # async with aiohttp.ClientSession(connector=self.conn) as session:
        try:
            while True:
                await self.get_proxy_pool()
                s = self.schedule_apkpure
                seed = await s.q.get()
                for parser in self.parsers:
                    if parser.level == seed.level:
                        await parser.parseResult(self, seed)
                s.q.task_done()

                """告诉队列 处理完毕"""
        except asyncio.CancelledError:
            pass


    async def get_proxy_pool(self):
        async with self.lock:
            if len(self.proxies) <= MIN_PROXY_COUNT:
                self.proxies = await self.crawlProxy.run(self.session)


