from aiohttp import web

from log_config import logger

routes = web.RouteTableDef()


@routes.view('/get_one')
class GetOne(web.View):
    async def get(self):
        conn = self.request.app['redis_conn']
        proxy = await conn.random()
        logger.info(f"now use {proxy}")
        return web.Response(text=f'{proxy}')


@routes.view('/count')
class Count(web.View):
    async def get(self):
        conn = self.request.app['redis_conn']
        count = await conn.get_count()
        logger.info(f"now proxies count: {count}")
        return web.Response(text=f'{count}')


@routes.view('/decrease/{proxy}')
class Decrease(web.View):
    async def get(self):
        proxy = self.request.match_info['proxy']
        conn = self.request.app['redis_conn']
        await conn.decrease(proxy)
        logger.info(f"{proxy} decreased")
        return web.Response(text=f'{proxy} decreased')
