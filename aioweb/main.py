from aiohttp import web

from db import redis_engine, background_tasks
from views import routes


async def app_factory():
    app = web.Application()
    app.cleanup_ctx.append(redis_engine)
    app.cleanup_ctx.append(background_tasks)
    app.add_routes(routes)
    return app


if __name__ == "__main__":
    web.run_app(app_factory())
