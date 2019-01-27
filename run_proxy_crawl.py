import subprocess
import random

from flask import Flask, g

from log_config import logger
from redis_client import RedisClient


app = Flask(__name__)


def get_conn():
    if not hasattr(g, 'redis'):
        g.redis = RedisClient()
    return g.redis


@app.route('/get_one')
def get_proxy():
    conn = get_conn()
    proxy = conn.random()
    logger.info(f'use {proxy}')
    return proxy


@app.route('/count')
def get_counts():
    conn = get_conn()
    count = conn.get_count()
    logger.info(f'there are {count} proxies')
    return f'{count}'


@app.route('/decrease/<proxy>')
def dec_proxy(proxy):
    conn = get_conn()
    conn.decrease(proxy)
    return f'{proxy} decreased'


@app.route('/crawl')
def fetch():
    p = subprocess.run(['scrapy', 'list'], stdout=subprocess.PIPE, encoding='utf8')
    name = random.choice(p.stdout.split())
    subprocess.run(['scrapy', 'crawl', name])
    return f'{name} crawl finish'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
