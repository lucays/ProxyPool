# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import redis

from aioweb.config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_KEY, INIT_SCORE


class ProxiesPipeline(object):

    def __init__(self):
        self.pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True)
        self.conn = redis.StrictRedis(connection_pool=self.pool)

    def process_item(self, item, spider):
        proxy = item['proxy']
        if not self.conn.zscore(REDIS_KEY, proxy):
            self.conn.zadd(REDIS_KEY, {proxy: INIT_SCORE})
        return item
