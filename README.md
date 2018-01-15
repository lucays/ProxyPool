# IPProxy-Spider
fetch free ip-proxies
抓取免费代理

# How To Use
安装好下面的软件包和模块
- Python3.6
- requests
```
pip install requests
```
- lxml
```
pip install lxml
```
然后在命令行的当前目录下运行
```
Python http_proxy.py
```
即可

# About sqlite3
没有做防注入，sqlite3在execute相关sql时似乎不能直接(sql, (...))，后来就懒得做了。

表名self.db_name是proxies, 包含2个字段：IP_PORT和valid

IP_PORT: ip代理，格式如127.0.0.1:8080，使用时还需要手动在前面加上http://

valid:对应的ip代理是否可用，1表示可用，0表示失效。

其实可以在失效时直接删除那个代理，但是在爬取代理网站时就容易出现重复验证大量数据库本来有但是因失效而删除的代理结果浪费时间的情况。所以多加了一个字段优化效率。

main()中是保证数据库有效代理大于12个的示例，当少于这个数值时重复爬取。
实际中一轮爬取大约会有200~300个有效代理入库。
完善的使用逻辑过段时间会放个有效的scrapy中间件上来作为示例。
