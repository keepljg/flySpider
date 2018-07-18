# _*_ coding: utf-8 _*_

# from queue import Queue
from config import URL_QUEUE_MAX_LENGTH
from asyncio import Queue

class Schedule():
    def __init__(self, loop):
        self.q = Queue(loop=loop, maxsize=URL_QUEUE_MAX_LENGTH)

    def InQueue(self, seed):
        """
        :param : seed is a list [url, try_time, url_level]
        :return: put seed to queue
        """
        self.q.put_nowait(seed)



class Seed(dict):
    def __init__(self, url, trytimes=0, level=1):
        super(Seed, self).__init__()
        self.url = str(url)
        self.trytimes = int(trytimes)
        self.level = int(level)
        self.data_type = 'normal'

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

        # 允许动态设置key的值，不仅仅可以d[k]，也可以d.k
    def __setattr__(self, key, value):
        self[key] = value