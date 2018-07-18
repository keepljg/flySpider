# _*_ coding: utf-8 _*_



import logging
import sys

"""mysql 配置"""
HOST = '192.168.182.118'
DATABASE = 'ios_app'
PORT = 3973
USER = 'deve'
PASSWORD = 'weiphone'
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
# PROXY_VERIFICATION_URL = 'http://baidu.com'
PROXY_VERIFICATION_URL = 'https://www.apple.com/shop/bag'

def get_logger(logname):
    Logger = logging.getLogger(logname)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
    # 控制台日志
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.formatter = formatter  # 也可以直接给formatter赋值

    # 为logger添加的日志处理器
    Logger.addHandler(console_handler)
    Logger.setLevel(logging.INFO)
    return Logger

normal = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36'
            }


detail = {
    'user-agent': 'iTunes/12.0.1 (Windows; Microsoft Windows 8 x64 Business Edition (Build 9200)) AppleWebKit/7600.1017.0.24'
}




