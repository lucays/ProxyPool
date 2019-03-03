
# IPProxy-Spider

fetch free ip-proxies
抓取免费代理

# How To Use

安装好下面的软件包和模块

- Python3.6+
- scrapy
- aioredis
- aiohttp

配置好aioweb/config.py的redis地址和密码

在aioweb中运行`python main.py`即可。

也可以用gunicorn，在这个目录下运行
`gunicorn main:app_factory --bind localhost:8080 --worker-class aiohttp.GunicornWebWorker`

请求`http://127.0.0.1:8080/proxy`即可获得随机代理。

# Example Codes

```python

'''
please set redis address & password in aioweb/config.py
then run:

python main.py

now you can use the following code to get proxy and delete proxy.
'''

import requests

# get proxy
url = 'http://127.0.0.1:8080/proxy'
proxy = requests.get(url).json()['proxy']

# get count
url = 'http://127.0.0.1:8080/count'
count = requests.get(url).json()['count']

# delete proxy
handle_url = f"http://127.0.0.1:8080/proxy/{proxy}"
resp = requests.delete(handle_url)

# add proxy
resp = requests.post(handle_url))

# set proxy's score to max
resp = requests.put(handle_url)

```
