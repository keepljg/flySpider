    # _*_ coding: utf-8 _*_

import asyncio
from threading import Thread
import requests
import urllib3
from datetime import datetime

from config import get_logger


urllib3.disable_warnings()
requests.packages.urllib3.disable_warnings()
#异步访问网页




# sem = asyncio.Semaphore(10)

logger = get_logger('asyncFetch')

class FilePath:
    @classmethod
    def file_path_detail(cls):
        now = datetime.now()
        now_date = now.strftime('%Y-%m-%d %H:%M:%S')
        FirstLevelDir = now_date.split(' ')[0]
        SecondLevelDir = now_date.split(' ')[1].split(':')[0]
        ThirdLevelDir = str(int(now_date.split(' ')[1].split(':')[1])/10)
        return FirstLevelDir, SecondLevelDir, ThirdLevelDir



class Fetcher(object):
    @classmethod
    async def fetch(cls, seed, session, headers, data_type='normal', proxy=None):
        try:
            print("url is {} proxy {}".format(seed.url, proxy))
            async with session.get(seed.url, headers=headers, proxy=proxy) as r:
                logger.info("get {} status_code is {}".format(seed.url, r.status))
                if r.status == 200:
                    if data_type == 'image':
                        data = await r.read()
                    else:
                        data = await r.text()
                    return data
                else:
                    logger.info("get {} is err: {}".format(seed.url, r.status))
                    return None
        except Exception as e:
            logger.info("err is {}".format(e))
            return None



