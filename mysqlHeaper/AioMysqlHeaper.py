# _*_ coding: utf-8 _*_
__time__ = '2018/5/16 11:57'
import aiomysql
from config import *

logger = logging.Logger(__name__)

class MysqlHeaper(object):
    """
    异步mysql class
    """
    async def get_pool(self, loop):
        self.pool = await aiomysql.create_pool(host=HOST, port=PORT,
                                               user=USER, password=PASSWORD,
                                               db=DATABASE, loop=loop, charset=CHARSET, autocommit=True)

    async def insert_into(self, sql, params):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                   results = await cur.execute(sql, params)
                   return results
                except Exception as e:
                    logger.exception(e)
                    return None

    async def fetch_all(self, sql, params):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(sql, params)
                    reconds = await cur.fetchall()
                    return reconds
                except Exception as e:
                    logger.exception(e)
                    return None

    async def fetch_one(self, sql, params):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    await cur.execute(sql, params)
                    recond = await cur.fetchone()
                    return recond
                except Exception as e:
                    logger.exception(e)
                    return None


    async def update(self, sql, params):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    reconds = await cur.execute(sql, params)
                    return reconds
                except Exception as e:
                    logger.exception(e)
                    return None

    async def execute(self, sql):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    reconds = await cur.execute(sql)
                    return reconds
                except Exception as e:
                    logger.exception(e)
                    return None

    def close_pool(self):
        self.pool.close()