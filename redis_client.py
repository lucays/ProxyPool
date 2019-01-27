# -*- coding: utf-8 -*-
# sudo vi /etc/redis/redis.conf
# sudo /etc/init.d/redis-server restart
# redis-cli -a redis321
import redis
import random

from config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_KEY, MAX_SCORE, MIN_SCORE, INIT_SCORE


class RedisClient:
    def __init__(self):
        self.pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True)
        self.conn = redis.StrictRedis(connection_pool=self.pool)

    def add(self, proxy):
        '''
        添加代理，分数设置为INIT_SCORE
        '''
        if not self.conn.zscore(REDIS_KEY, proxy):
            return self.conn.zadd(REDIS_KEY, INIT_SCORE, proxy)

    def random(self):
        '''
        随机获取代理
        首先尝试获取分数为MAX_SCORE的代理
        最高分不存在则按排名获取
        '''
        result = self.conn.zrangebyscore(REDIS_KEY, MAX_SCORE, MAX_SCORE)
        if len(result):
            return random.choice(result)
        else:
            result = self.conn.zrevrange(REDIS_KEY, 0, 100)
            if len(result):
                return random.choice(result)

    def decrease(self, proxy):
        '''
        对代理分数-1
        如果分数小于MIN_SCORE，移除
        '''
        score = self.conn.zscore(REDIS_KEY, proxy)
        if score and score > MIN_SCORE:
            return self.conn.zincrby(REDIS_KEY, proxy, -1)
        else:
            return self.conn.zrem(REDIS_KEY, proxy)

    def is_exist(self, proxy):
        '''
        判断是否存在
        '''
        return not self.conn.zscore(REDIS_KEY, proxy) is None

    def score2max(self, proxy):
        '''
        把代理分数设为MAX_SCORE
        '''
        return self.conn.zadd(REDIS_KEY, MAX_SCORE, proxy)

    def get_count(self):
        '''
        获取代理总数
        '''
        return self.conn.zcard(REDIS_KEY)

    def get_all(self):
        '''
        获取全部代理
        '''
        return self.conn.zrangebyscore(REDIS_KEY, MIN_SCORE, MAX_SCORE)
