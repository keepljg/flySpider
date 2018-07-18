# _*_ coding: utf-8 _*_

import asyncio
import re
import time
from asyncio import Lock
from lxml import etree

from config import PROXY_TYPE, PROXY_VERIFICATION_URL, CRAWL_PROXY_TIME
from config import get_logger

LOGGER = get_logger(__name__)


lock = Lock()
class asyncCrawlProxy():
    def __init__(self, loop=None):
        self.loop = loop or asyncio.get_event_loop()
        self.headers_foreign_gather = {
            'Host': "www.gatherproxy.com",  # 需要修改为当前网站主域名
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36",
        }

        self.headers_foreign_other = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.5',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'www.us-proxy.org',
            'If-Modified-Since': 'Tue, 24 Jan 2017 03:32:01 GMT',
            'Referer': 'http://www.sslproxies.org/',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36"
        }
        self.headers_cn_xici = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.5',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'www.xicidaili.com',
            'If-None-Match': 'W/"cb655e834a031d9237e3c33f3499bd34"',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36",
        }


    async def get_cn_proxy_cn(self, session, proxies):
        urls = ['http://www.xicidaili.com/nn/%s' % n for n in range(1, 6)]
        for url in urls:
            html_code = await self.get_request(url, session, self.headers_cn_xici)
            if html_code:
                proxy_list_json = self.xpath_html_code_xici(html_code)
                if proxy_list_json:
                    for proxy_info in proxy_list_json:
                        proxies.add(proxy_info)

    def xpath_html_code_xici(self, html_code):
        html = etree.HTML(html_code)
        proxy_list_json = []
        infos = html.xpath('//tr[@class="odd"]')
        for i, info in enumerate(infos):
            PROXY_IP = info.xpath('//td[2]/text()')[0]
            PROXY_PORT = info.xpath('//td[3]/text()')[0]
            tuple_i = (PROXY_IP, PROXY_PORT)
            proxy_list_json.append(tuple_i)
        return proxy_list_json


    async def get_foreign_proxy_gather(self, session, proxies):
        url = "http://www.gatherproxy.com"
        html_code = await self.get_request(url, session, self.headers_foreign_gather)

        proxy_list_json = self.re_html_code_gather(html_code)
        if proxy_list_json:
            for proxy_info in proxy_list_json:
                proxies.add(proxy_info)

    def re_html_code_gather(self, html_code):
        proxy_list_json = []
        re_str = '(?<=insertPrx\().*\}'
        proxy_list = re.findall(re_str, html_code)
        null = ''
        for i in proxy_list:
            json_list = eval(i)

            PROXY_IP = json_list['PROXY_IP']
            PROXY_PORT = json_list['PROXY_PORT']
            PROXY_PORT = int(PROXY_PORT, 16)

            tuple_i = (PROXY_IP, PROXY_PORT)

            proxy_list_json.append(tuple_i)

        return proxy_list_json

    async def get_foreign_proxy_other(self, session, proxies):
        proxy_list_json = []
        urls = [
            # 'http://www.sslproxies.org/',
            'http://www.us-proxy.org/',
            'http://free-proxy-list.net/uk-proxy.html',
            # 'http://www.socks-proxy.net/',
        ]
        for url in urls:
            html_code = await self.get_request(url, session, self.headers_foreign_other)
            proxy_list_json = self.re_html_code_other(html_code, proxy_list_json)
            if proxy_list_json:
                for proxy_info in proxy_list_json:
                    proxies.add(proxy_info)

    def re_html_code_other(self, html_code, pro_list_json):
        pattern = re.compile(
            '<tr><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td.+?>(.*?)</td><td>(.*?)</td><td.+?>(.*?)</td><td.+?>(.*?)</td><td.+?>(.*?)</td></tr>',
            re.S)
        items = re.findall(pattern, html_code)
        if items is not None:
            for item in items:
                PROXY_IP = item[0]
                PROXY_PORT = item[1]
                tuple_i = (PROXY_IP, PROXY_PORT)
                pro_list_json.append(tuple_i)
            return pro_list_json


    async def get_request(self, url, session, headers):
        '''参数引入及头信息'''
        async with session.get(url, headers=headers) as r:
            print('get {} status_code is {}'.format(url, r.status))
            if r.status == 200:
                data = await r.text()
                return data


    async def get_ori_proxy(self, session, proxies):
        if PROXY_TYPE == 1:
            tasks = [asyncio.ensure_future(self.get_foreign_proxy_gather(session, proxies)),
                     asyncio.ensure_future(self.get_foreign_proxy_other(session, proxies))]
        else:
            tasks = [asyncio.ensure_future(self.get_cn_proxy_cn(session, proxies))]

        await asyncio.gather(*tasks)

    async def check_from_itunes(self, session, proxy_info):
        proxy = 'http://' + str(proxy_info[0]) + ':' + str(proxy_info[1])
        LOGGER.info("is checking proxy {}".format(proxy))
        headers_normal = {
            'User_Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36',
        }
        try:
            start_time = time.time()
            async with session.get(url=PROXY_VERIFICATION_URL,
                                   proxy=proxy,
                                   headers=headers_normal,  # 可以引用到外部的headers
                                   timeout=CRAWL_PROXY_TIME) as resp:
                LOGGER.info("{} is status_code is {}".format(proxy, resp.status))
                if resp.status == 200:
                    LOGGER.info("{} is check success use time is {}".format(proxy, time.time() - start_time))
                    return proxy
                else:
                    LOGGER.info("{} is check failed".format(proxy))
                    return None

        except:
            LOGGER.info("{} is check failed".format(proxy))
            return None
            # proxies.remove(proxy_info)


    async def get_useful_proxy(self, session):
        proxies = set()
        await self.get_ori_proxy(session, proxies)
        tasks = []
        for proxy in proxies:
            tasks.append(asyncio.ensure_future(self.check_from_itunes(session, proxy)))
        return await asyncio.gather(*tasks)


    async def run(self, session):
        proxies = []
        results = await self.get_useful_proxy(session)
        for result in results:
            if result != None:
                proxies.append(result)
        # await asyncio.gather(*tasks)

        return proxies

#

