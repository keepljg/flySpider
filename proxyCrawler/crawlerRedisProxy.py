# _*_ coding: utf-8 _*_


import asyncio

import aiohttp

import redis
import re

from aiohttp.client_exceptions import ClientConnectionError
from aiohttp.client_exceptions import ServerTimeoutError
from queue import Queue
import redis
from lxml import etree
import re
from datetime import datetime
import time
from config import get_logger

LOGGER = get_logger(__name__)


proxies = set()
headers_gather = {
    'Host': "www.gatherproxy.com",  # 需要修改为当前网站主域名
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36",
}

headers_other = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.5',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'www.us-proxy.org',
        'If-Modified-Since': 'Tue, 24 Jan 2017 03:32:01 GMT',
        'Referer': 'http://www.sslproxies.org/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:50.0) Gecko/20100101 Firefox/50.0',
    }


async def check_from_itunes(session, proxy_info):
    global proxies
    proxy = 'http://' + str(proxy_info[0]) + ':' + str(proxy_info[1])
    headers_normal = {
        'User_Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36',
    }
    try:
        async with session.get(url='https://www.apple.com/shop/bag',
                               proxy=proxy,
                               headers=headers_normal,  # 可以引用到外部的headers
                               timeout=20) as resp:
            if resp.status == 200:
                LOGGER.info("{} is check success".format(proxy))
            else:
                LOGGER.info("{} is check failed".format(proxy))
                proxies.remove(proxy_info)

    except:
        LOGGER.info("{} is check failed".format(proxy))
        proxies.remove(proxy_info)


async def get_proxy_gather(session):
    url = "http://www.gatherproxy.com"
    html_code = await get_request(url, session, headers_gather)
    proxy_list_json = re_html_code_gather(html_code)
    if proxy_list_json:
        global proxies
        for proxy_info in proxy_list_json:
            proxies.add(proxy_info)
        return proxies

def re_html_code_gather(html_code):
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



async def get_proxy_other(session):
    proxy_list_json = []
    urls = [
        # 'http://www.sslproxies.org/',
        'http://www.us-proxy.org/',
        'http://free-proxy-list.net/uk-proxy.html',
        # 'http://www.socks-proxy.net/',
    ]
    for url in urls:
        html_code = await get_request(url, session, headers_other)
        proxy_list_json = re_html_code_other(html_code, proxy_list_json)
        if proxy_list_json:
            global proxies
            for proxy_info in proxy_list_json:
                proxies.add(proxy_info)
            return proxies


def re_html_code_other(html_code, pro_list_json):
    pattern = re.compile(
        '<tr><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td.+?>(.*?)</td><td>(.*?)</td><td.+?>(.*?)</td><td.+?>(.*?)</td><td.+?>(.*?)</td></tr>',
        re.S)
    items = re.findall(pattern, html_code)
    if items is not None:
        for item in items:
            PROXY_IP=item[0]
            PROXY_PORT=item[1]
            tuple_i = (PROXY_IP, PROXY_PORT)
            pro_list_json.append(tuple_i)
        return pro_list_json


async def get_request(url, session, headers):
    '''参数引入及头信息'''
    async with session.get(url, headers=headers) as r:
        # print(r.status)
        if r.status == 200:
            data = await r.text()
            return data




async def checkProxies(loop):
    global proxies
    conn = aiohttp.TCPConnector(verify_ssl=False,
                                use_dns_cache=True)
    async with aiohttp.ClientSession(loop=loop, connector=conn) as session:
        await get_proxy_gather(session)
        await get_proxy_other(session)
        tasks = []
        # print(proxies)
        LOGGER.info("before check proxy is {}".format(proxies))
        for proxy in proxies:
            tasks.append(asyncio.ensure_future(check_from_itunes(session, proxy)))


        await asyncio.wait(tasks)


def get_proxy():
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(checkProxies(loop))
    loop.run_until_complete(future)
    LOGGER.info("after check proxy is {}".format(proxies))


def run():

    global proxies
    # job_redis = redis.Redis(host='localhost')
    ios_redis = redis.Redis(host='127.0.0.1', port=6379)
    # mysql_heaper = MySql()
    while True:
        proxy_len = ios_redis.scard('iosUpdateProxy')
        if proxy_len < 15:
            get_proxy()
            for proxy in proxies:
                proxy = 'http://' + str(proxy[0]) + ':' + str(proxy[1])
                ios_redis.sadd('Proxy', proxy)
            proxies.clear()
        time.sleep(5)



if __name__ == '__main__':
    run()