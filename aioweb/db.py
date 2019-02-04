import subprocess
import asyncio
import os

import aiohttp

from aioredis_client import RedisClient
from log_config import logger
from config import TEST_URL, HEADERS, TIMEOUT, BATCH_TEST_SIZE


class cd:
    """
    改变目前工作区文件夹路径的上下文管理器
    """
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


class ProxyTester:

    async def proxy_test(self, app, session, proxy):
        real_proxy = 'http://' + proxy
        try:
            async with session.get(TEST_URL, headers=HEADERS, proxy=real_proxy, timeout=TIMEOUT) as resp:
                if resp.status == 200:
                    logger.info(f'{proxy} test useful')
                    await app['redis_conn'].score2max(proxy)
                else:
                    logger.info(f'{proxy} status code error: {resp.status}')
                    await app['redis_conn'].decrease(proxy)
                await asyncio.sleep(0.5)
        except Exception as e:
            logger.info(f'{proxy} test invalid')
            await app['redis_conn'].decrease(proxy)

    async def all_proxies_test(self, app, proxies):
        async with aiohttp.ClientSession() as session:
            if len(proxies) > BATCH_TEST_SIZE:
                for i in range(0, len(proxies), BATCH_TEST_SIZE):
                    test_proxies = proxies[i: i+BATCH_TEST_SIZE]
                    asyncio.gather(*[self.proxy_test(app, session, proxy) for proxy in test_proxies])
            else:
                asyncio.gather(*[self.proxy_test(app, session, proxy) for proxy in proxies])


async def redis_engine(app):
    app['redis_conn'] = await RedisClient.create()
    yield
    await app['redis_conn'].close()


async def crawl_proxies(app):
    while True:
        await asyncio.sleep(3)
        with cd("../"):
            logger.info(f'now in {os.getcwd()}')
            """
            # 这两行代码在Python3.6尚未实现，需要Python3.7才能运行
            process = await asyncio.create_subprocess_exec('scrapy list', stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await process.communicate()
            """
            p = subprocess.run(['scrapy', 'list'], stdout=subprocess.PIPE, encoding='utf8')
            spiders = p.stdout.split()

            for spider in spiders:
                logger.info(spider)
                try:
                    subprocess.run(['scrapy', 'crawl', spider], timeout=60*10)
                except subprocess.TimeoutExpired as e:
                    logger.error(f'{spider} crawl TIMEOUT!')
                await asyncio.sleep(3)
        await asyncio.sleep(3600*3)


async def proxies_test(app):
    while True:
        # await asyncio.sleep(3600*3)
        conn = app['redis_conn']
        proxies = await conn.get_all()
        proxytester = ProxyTester()
        logger.info(f"proxies count: {len(proxies)}")
        await proxytester.all_proxies_test(app, proxies)
        await asyncio.sleep(3600*5)


async def background_tasks(app):
    app['crawl_proxies'] = app.loop.create_task(crawl_proxies(app))
    app['proxies_test'] = app.loop.create_task(proxies_test(app))
    yield
    app['proxies_test'].cancel()
    # await app['proxies_test']
    app['crawl_proxies'].cancel()
    # await app['crawl_proxies']
