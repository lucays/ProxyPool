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
    sucess_count = 0

    async def proxy_test(self, app, session, proxy):
        real_proxy = 'http://' + proxy
        try:
            async with session.get(TEST_URL, headers=HEADERS, proxy=real_proxy, timeout=TIMEOUT) as resp:
                if resp.status == 200:
                    logger.info(f'{proxy} test useful')
                    await app['redis_client'].score2max(proxy)
                    self.sucess_count += 1
                else:
                    logger.info(f'{proxy} status code error: {resp.status}')
                    await app['redis_client'].decrease(proxy)
                await asyncio.sleep(0.5)
        except Exception as e:
            logger.info(f'{proxy} test invalid')
            await app['redis_client'].decrease(proxy)

    async def all_proxies_test(self, app, proxies):
        async with aiohttp.ClientSession() as session:
            if len(proxies) > BATCH_TEST_SIZE:
                for i in range(0, len(proxies), BATCH_TEST_SIZE):
                    test_proxies = proxies[i: i+BATCH_TEST_SIZE]
                    await asyncio.gather(*[self.proxy_test(app, session, proxy) for proxy in test_proxies])
            else:
                await asyncio.gather(*[self.proxy_test(app, session, proxy) for proxy in proxies])
        return self.sucess_count


async def redis_engine(app):
    app['redis_client'] = await RedisClient.create()
    yield
    await app['redis_client'].close()


async def crawl_proxies(app):
    proxies_count = await app['redis_client'].get_count()
    logger.info(f"now there are {proxies_count} proxies.")
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
        proxies_count = await app['redis_client'].get_count()
        await asyncio.sleep(3600*0.5)


async def proxies_test(app):
    while True:
        await asyncio.sleep(0.1)
        redis_client = app['redis_client']
        proxies = await redis_client.get_all()
        logger.info(f"proxies count: {len(proxies)}")
        proxytester = ProxyTester()
        sucess_count = await proxytester.all_proxies_test(app, proxies)
        logger.info(f"proxies valid count: {sucess_count}")
        await asyncio.sleep(3600*0.2)


async def background_tasks(app):
    app['crawl_proxies'] = app.loop.create_task(crawl_proxies(app))
    app['proxies_test'] = app.loop.create_task(proxies_test(app))
    yield
    app['proxies_test'].cancel()
    app['crawl_proxies'].cancel()
