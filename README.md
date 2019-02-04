
# IPProxy-Spider

fetch free ip-proxies
抓取免费代理

# How To Use

安装好下面的软件包和模块

- Python3.6+
- scrapy
- redis
- aioredis
- aiohttp
  
配置好config.py的redis地址和密码

在aioweb中运行`python main.py`即可。

也可以用gunicorn，在这个目录下运行
`gunicorn main:app_factory --bind localhost:8080 --worker-class aiohttp.GunicornWebWorker`

请求`http://127.0.0.1:8080/get_one`即可获得随机代理。
