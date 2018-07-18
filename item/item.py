# _*_ coding: utf-8 _*_

from selector.selector import Selector, Xpath
from config import get_logger
logger = get_logger(__name__)

class ItemMetaclass(type):
    """
     __new__方法接受的参数依次是：
    1.当前准备创建的类的对象（cls）
    2.类的名字（name）
    3.类继承的父类集合(bases)
    4.类的方法集合(attrs)
    """
    def __new__(cls, name, bases, attrs):
        if name == 'Selector':
            """不能选择基类选择器"""
            return type.__new__(cls, name, bases, attrs)
        selectors = {}
        for k, v in attrs.items():
            if isinstance(v, Selector):
                selectors[k] = v
            # 结合之前，即把之前在方法集合中的零散的映射删除，
            # 把它们从方法集合中挑出，组成一个大方法__selectors__
            # 把__selectors__添加到方法集合attrs中
        for k in selectors.keys():
            attrs.pop(k)
        attrs['selectors'] = selectors
        return type.__new__(cls, name, bases, attrs)


class Item(metaclass=ItemMetaclass):
    def __init__(self, html):
        self.results = {}
        for k, selector in self.selectors.items():
            value = selector.parse_detail(html)
            if value is None:
                logger.error('Selector "{}" for {} was wrong, please check again'.format(selector.rule, name))
            else:
                self.results[k] = value
            print(self.results)

    def save(self):
        if hasattr(self, '__result__'):
            self.__result__.save(self.results)
            # return self.results
        else:
            raise NotImplementedError

    async def detail(self, arg):
        pass


    def get_results(self):
        return self.results

    def __repr__(self):
        return '<item {}>'.format(self.results)
        # return self.results


    # 让获取key的值不仅仅可以d[k]，也可以d.k
    def __getitem__(self, key):
        try:
            return self.results[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    # 允许动态设置key的值，不仅仅可以d[k]，也可以d.k
    def __setitem__(self, key, value):
        self.results[key] = value

import requests
if __name__ == '__main__':
    html = requests.get("http://www.baidu.com").text
    class urlItem(Item):
        title = Xpath("//input[@id='su']/@value")

    item = urlItem(html)
    print(item['title'])
