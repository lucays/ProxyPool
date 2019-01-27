# -*- coding: utf-8 -*-
import subprocess
import time
import asyncio

import aiohttp

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
                async with session.get(TEST_URL, proxy=real_proxy, headers=HEADERS, timeout=TIMEOUT) as r:
                    if r.status == 200:
                        logger.info(f'{proxy} useful')
                        self.redis.score2max(proxy)
                    else:
                        logger.info(f'{proxy} status code error: {r.status}')
                        self.redis.decrease(proxy)
                    await asyncio.sleep(0.5)
            except Exception:
                logger.info(f'{proxy} invalid:')
                self.redis.decrease(proxy)

    def run(self):
        '''
        测试主函数
        '''
        logger.info('start to test proxies')
        proxies = self.redis.get_all()
        loop = asyncio.get_event_loop()
        if len(proxies) > BATCH_TEST_SIZE:
            for i in range(0, len(proxies), BATCH_TEST_SIZE):
                test_proxies = proxies[i: i+BATCH_TEST_SIZE]
                tasks = [self.test_proxy(proxy) for proxy in test_proxies]
                loop.run_until_complete(asyncio.wait(tasks))
        else:
            tasks = [self.test_proxy(proxy) for proxy in proxies]
            loop.run_until_complete(asyncio.wait(tasks))


def func():
    p = subprocess.run(['scrapy', 'list'], stdout=subprocess.PIPE, encoding='utf8')
    r = p.stdout
    for name in r.split():
        logger.info(name)
        subprocess.run(['scrapy', 'crawl', name])


def main():
    while True:
        func()
        logger.info('one crawl finish')
        obj = Tester()
        obj.run()
        logger.info('test finish')
        time.sleep(3600*3.3)


if __name__ == '__main__':
    main()
