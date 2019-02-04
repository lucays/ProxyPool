from aiohttp import web

routes = web.RouteTableDef()


@routes.view('/get_one')
class GetOne(web.View):
    async def get(self):
        conn = self.request.app['redis_conn']
        proxy = await conn.random()
        return web.Response(text=f'{proxy}')


@routes.view('/count')
class Count(web.View):
    async def get(self):
        conn = self.request.app['redis_conn']
        count = await conn.get_count()
        return web.Response(text=f'{count}')


@routes.view('/decrease/{proxy}')
class Decrease(web.View):

    async def get(self):
        proxy = self.request.match_info['proxy']
        conn = self.request.app['redis_conn']
        await conn.decrease(proxy)
        return web.Response(text=f'{proxy} decreased')
