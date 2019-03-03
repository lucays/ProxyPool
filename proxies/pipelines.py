# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import asyncio

from aioweb.aioredis_client import RedisClient


class ProxiesPipeline(object):

    def __init__(self):
        pass

    async def add(self, proxy):
        conn = await RedisClient.create()
        await conn.add(proxy)

    def process_item(self, item, spider):
        proxy = item['proxy']
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.add(proxy))
        return item
