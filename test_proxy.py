# -*- coding: utf-8 -*-
import traceback
import aiohttp
import asyncio

from config import HEADERS, BATCH_TEST_SIZE, TIMEOUT, TEST_URL
from redis_client import RedisClient
from log_config import logger


class Tester:
    def __init__(self):
        self.redis = RedisClient()

    async def test_proxy(self, proxy):
        '''
        测试单个代理是否可用
        '''
        real_proxy = 'http://' + proxy
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(TEST_URL, proxy=real_proxy, headers=HEADERS, timeout=TIMEOUT, verify=False) as r:
                    if r.status == 200:
                        logger.info(f'{proxy} useful')
                        self.redis.score2max(proxy)
                    else:
                        logger.info(f'{proxy} status code error')
                        self.redis.decrease(proxy)
            except Exception:
                logger.info(f'{proxy} request fail')
                self.redis.decrease(proxy)

    def run(self):
        '''
        测试主函数
        '''
        logger.info('start to test proxies')
        try:
            proxies = self.redis.get_all()
            loop = asyncio.get_event_loop()
            for i in range(0, len(proxies), BATCH_TEST_SIZE):
                test_proxies = proxies[i: i+BATCH_TEST_SIZE]
                tasks = [self.test_proxy(proxy) for proxy in test_proxies]
                loop.run_until_complete(asyncio.wait(tasks))
        except Exception:
            traceback.print_exc()
