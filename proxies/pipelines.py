# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import asyncio
import concurrent

import aiohttp

from config import HEADERS, TEST_URL, TIMEOUT
from log_config import logger
from redis_client import RedisClient


class ProxiesPipeline(object):
    def __init__(self):
        self.redis = RedisClient()
        self.old_proxies = set(self.redis.get_all())
        self.loop = asyncio.get_event_loop()

    async def _fetch(self, session, url, proxy):
        try:
            async with session.get(url, proxy=proxy, headers=HEADERS, timeout=TIMEOUT) as r:
                if r.status == 200:
                    logger.info(f'{proxy} useful')
                    self.redis.add(proxy)
                    self.redis.score2max(proxy)
                else:
                    logger.info(f'{proxy} status code error: {r.status}')
        except (concurrent.futures._base.TimeoutError, aiohttp.client_exceptions.ClientProxyConnectionError, ConnectionRefusedError):
            logger.info(f'{proxy} invalid')
        except Exception:
            logger.exception(f'{proxy} invalid:')

    async def test_proxy(self, proxy):
        '''
        测试单个代理是否可用
        '''
        real_proxy = 'http://' + proxy
        async with aiohttp.ClientSession() as session:
            datas = await asyncio.gather(*[self._fetch(session, TEST_URL, real_proxy)])
            return datas

    def process_item(self, item, spider):
        proxy = item['proxy']
        if proxy not in self.old_proxies:
            self.loop.run_until_complete(self.test_proxy(proxy))
            return item
