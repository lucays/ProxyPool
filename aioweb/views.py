from aiohttp import web

from log_config import logger

routes = web.RouteTableDef()


@routes.view('/proxy')
class Proxy(web.View):
    async def get(self):
        '''
        随机获取1个分数最高的代理
        '''
        conn = self.request.app['redis_conn']
        proxy = await conn.random()
        logger.info(f"now use {proxy}")
        return web.Response(text=f'{proxy}')


@routes.view('/count')
class Count(web.View):
    async def get(self):
        '''
        获取代理总数
        '''
        conn = self.request.app['redis_conn']
        count = await conn.get_count()
        logger.info(f"now proxies count: {count}")
        return web.Response(text=f'{count}')


@routes.view('/proxy/{proxy}')
class HandleProxy(web.View):
    async def post(self):
        '''
        添加1个代理
        '''
        proxy = self.request.match_info['proxy']
        conn = self.request.app['redis_conn']
        await conn.add(proxy)
        info = f"{proxy} added."
        logger.info(info)
        return web.Response(text=info)

    async def put(self):
        '''
        更新代理分数为最大值
        '''
        proxy = self.request.match_info['proxy']
        conn = self.request.app['redis_conn']
        await conn.score2max(proxy)
        info = f"{proxy} score set to max."
        logger.info(info)
        return web.Response(text=info)

    async def delete(self):
        '''
        代理分数-1
        如果分数小于MIN_SCORE，移除
        '''
        proxy = self.request.match_info['proxy']
        conn = self.request.app['redis_conn']
        await conn.decrease(proxy)
        info = f"{proxy} decreased."
        logger.info(info)
        return web.Response(text=info)
