# -*- coding: utf-8 -*-
# sudo vi /etc/redis/redis.conf
# sudo /etc/init.d/redis-server restart
# redis-cli -a redis321
import sys
import asyncio
import random

import aioredis

sys.path.append("..")

from config import REDIS_HOST, REDIS_PASSWORD, REDIS_KEY, MAX_SCORE, MIN_SCORE, INIT_SCORE


class RedisClient:
    @classmethod
    async def create(cls):
        """
        __init__不能是协程，写成工厂函数
        """
        self = cls()
        self.pool = await aioredis.create_redis_pool(address=f"redis://{REDIS_HOST}", password=REDIS_PASSWORD, encoding='utf-8')
        self.conn = await self.pool
        return self

    async def add(self, proxy):
        '''
        添加代理，分数设置为INIT_SCORE
        '''
        if not await self.conn.zscore(REDIS_KEY, proxy):
            return await self.conn.zadd(REDIS_KEY, INIT_SCORE, proxy)

    async def random(self):
        '''
        随机获取代理
        首先尝试获取分数为MAX_SCORE的代理
        最高分不存在则按排名获取
        '''
        result = await self.conn.zrangebyscore(REDIS_KEY, MAX_SCORE, MAX_SCORE)
        if len(result):
            return random.choice(result)
        else:
            result = await self.conn.zrevrange(REDIS_KEY, 0, 100)
            if len(result):
                return random.choice(result)

    async def decrease(self, proxy):
        '''
        对代理分数-1
        如果分数小于MIN_SCORE，移除
        '''
        score = await self.conn.zscore(REDIS_KEY, proxy)
        if score and score > MIN_SCORE:
            return await self.conn.zincrby(REDIS_KEY, -1, proxy)
        else:
            return await self.conn.zrem(REDIS_KEY, proxy)

    async def delete(self, proxy):
        return await self.conn.zrem(REDIS_KEY, proxy)

    async def is_exist(self, proxy):
        '''
        判断是否存在
        '''
        return not await self.conn.zscore(REDIS_KEY, proxy) is None

    async def score2max(self, proxy):
        '''
        把代理分数设为MAX_SCORE
        '''
        return await self.conn.zadd(REDIS_KEY, MAX_SCORE, proxy)

    async def get_count(self):
        '''
        获取代理总数
        '''
        return await self.conn.zcard(REDIS_KEY)

    async def get_all(self):
        '''
        获取全部代理
        '''
        return await self.conn.zrangebyscore(REDIS_KEY, MIN_SCORE, MAX_SCORE)

    async def close(self):
        self.conn.close()
        self.pool.close()
        await self.conn.wait_closed()
        await self.pool.wait_closed()


async def main():
    r = await RedisClient.create()
    counts = await r.get_count()
    print(counts)
    return counts

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
