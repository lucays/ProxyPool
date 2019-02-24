from aiohttp import web

from log_config import logger

routes = web.RouteTableDef()


@routes.view('/proxy')
class GetOne(web.View):
    async def get(self):
        conn = self.request.app['redis_conn']
        proxy = await conn.random()
        logger.info(f"now use {proxy}")
        return web.Response(text=f'{proxy}')

    async def delete(self):
        post = await self.request.post()
        proxies = post.values()
        conn = self.request.app['redis_conn']
        for proxy in proxies:
            await conn.decrease(proxy)
            logger.info(f"{proxy} decreased")
        return web.Response(text=f'{proxies} decreased')


@routes.view('/count')
class Count(web.View):
    async def get(self):
        conn = self.request.app['redis_conn']
        count = await conn.get_count()
        logger.info(f"now proxies count: {count}")
        return web.Response(text=f'{count}')
