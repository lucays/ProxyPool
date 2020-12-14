from aiohttp import web

routes = web.RouteTableDef()


@routes.view('/proxy')
class Proxy(web.View):
    async def get(self):
        '''
        随机获取1个分数最高的代理
        '''
        redis_client = self.request.app['redis_client']
        proxy = await redis_client.random()
        return web.json_response({'proxy': proxy})

    async def post(self):
        '''
        添加1个代理
        '''
        proxy = (await self.request.post())['proxy']
        redis_client = self.request.app['redis_client']
        await redis_client.add(proxy)
        score = await redis_client.get_score(proxy)
        return web.json_response({'proxy': proxy, 'score': score})


@routes.view('/count')
class Count(web.View):
    async def get(self):
        '''
        获取代理总数
        '''
        redis_client = self.request.app['redis_client']
        count = await redis_client.get_count()
        return web.json_response({'count': count})


@routes.view('/proxy/{proxy}')
class HandleProxy(web.View):

    async def get(self):
        '''
        检查是否存在，如果存在返回分数
        '''
        proxy = self.request.match_info['proxy']
        redis_client = self.request.app['redis_client']
        status = await redis_client.is_exist(proxy)
        score = -1
        if status:
            score = await redis_client.get_score(proxy)
        return web.json_response({'status': status, 'score': score})

    async def put(self):
        '''
        更新代理分数为最大值
        '''
        proxy = self.request.match_info['proxy']
        redis_client = self.request.app['redis_client']
        await redis_client.score2max(proxy)
        score = await redis_client.get_score(proxy)
        return web.json_response({'proxy': proxy, 'score': score})

    async def delete(self):
        '''
        移除代理
        '''
        proxy = self.request.match_info['proxy']
        redis_client = self.request.app['redis_client']
        await redis_client.delete(proxy)
        return web.json_response({'status': 'success'})
