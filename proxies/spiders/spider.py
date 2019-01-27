# -*- coding: utf-8 -*-
import scrapy
from ..items import ProxiesItem


class KuaidailiSpider(scrapy.Spider):
    name = 'kuaidaili'
    start_urls = [f'https://www.kuaidaili.com/free/inha/{i}/' for i in range(1, 3)]

    def parse(self, response):
        ips = response.xpath('//div[@id="list"]/table/tbody/tr/td[@data-title="IP"]/text()').extract()
        ports = response.xpath('//div[@id="list"]/table/tbody/tr/td[@data-title="PORT"]/text()').extract()
        for ip, port in zip(ips, ports):
            item = ProxiesItem()
            item['proxy'] = f'{ip}:{port}'
            yield item


class XiciSpider(scrapy.Spider):
    name = 'xici'
    start_urls = [f'http://www.xicidaili.com/nn/{i}' for i in range(1, 3)]

    def parse(self, response):
        ips = response.xpath('//tr[@class="odd"]/td[2]/text()').extract()
        ports = response.xpath('//tr[@class="odd"]/td[3]/text()').extract()
        for ip, port in zip(ips, ports):
            item = ProxiesItem()
            item['proxy'] = f'{ip}:{port}'
            yield item


class MimvpSpider(scrapy.Spider):
    name = 'mimvp'
    start_urls = ['https://proxy.mimvp.com/free.php?proxy=in_hp']

    def parse(self, response):
        ips = response.xpath('//div[@class="free-list"]/table/tbody/td[@class="tbl-proxy-ip"]/text()').extract()
        for ip in ips:
            item = ProxiesItem()
            for port in (80, 8060, 8090):
                item['proxy'] = f'{ip}:{port}'
                yield item


class _66ipSpider(scrapy.Spider):
    name = '_66ip'
    start_urls = ['http://www.66ip.cn/nmtq.php?getnum=512&isp=0&anonymoustype=0&start=&ports=&export=&ipaddress=&area=0&proxytype=2&api=66ip']

    def parse(self, response):
        proxies = [i.strip() for i in response.xpath('//text()').extract() if ':' in i]
        for proxy in proxies:
            item = ProxiesItem()
            item['proxy'] = proxy
            yield item


class _3366ipSpider(scrapy.Spider):
    name = '_3366ip'
    start_urls = [f'http://www.ip3366.net/free/?stype=1&page={i}' for i in range(1, 3)]

    def parse(self, response):
        tmp = [i for i in response.xpath('//tbody/tr/td/text()').extract()]
        datas = [i for i in tmp if i.isdigit() or ''.join(i.split('.')).isdigit()]
        for ip, port in zip(datas[::2], datas[1::2]):
            item = ProxiesItem()
            item['proxy'] = f'{ip}:{port}'
            yield item


class MimiipSpider(scrapy.Spider):
    name = 'mimiip'
    start_urls = [f'http://www.mimiip.com/gngao/{i}' for i in range(1, 3)]

    def parse(self, response):
        tmp = [i for i in response.xpath('//table/tr/td/text()').extract()]
        datas = [i for i in tmp if i.isdigit() or ''.join(i.split('.')).isdigit()]
        for ip, port in zip(datas[::2], datas[1::2]):
            item = ProxiesItem()
            item['proxy'] = f'{ip}:{port}'
            yield item


class Data5uSpider(scrapy.Spider):
    name = 'data5u'
    start_urls = ['http://www.data5u.com/free/gngn/index.shtml']

    def parse(self, response):
        tmp = [i for i in response.xpath('//ul[@class="l2"]/span/li/text()').extract()]
        datas = [i for i in tmp if i and (i.isdigit() or ''.join(i.split('.')).isdigit())]
        for ip, port in zip(datas[::2], datas[1::2]):
            item = ProxiesItem()
            item['proxy'] = f'{ip}:{port}'
            yield item


class Ip181Spider(scrapy.Spider):
    name = 'ip181'
    start_urls = ['http://www.ip181.com/']

    def parse(self, response):
        tmp = [i for i in response.xpath('//tbody/tr/td').extract()]
        datas = [i for i in tmp if i and (i.isdigit() or ''.join(i.split('.')).isdigit())]
        for ip, port in zip(datas[::2], datas[1::2]):
            item = ProxiesItem()
            item['proxy'] = f'{ip}:{port}'
            yield item


class Kxdaili(scrapy.Spider):
    name = 'kxdaili'
    start_urls = [f'http://www.kxdaili.com/dailiip/1/{i}.html#ip' for i in range(1, 3)]

    def parse(self, response):
        tmp = [i for i in response.xpath('//tbody/tr/td').extract()]
        datas = [i for i in tmp if i and (i.isdigit() or ''.join(i.split('.')).isdigit())]
        for ip, port in zip(datas[::2], datas[1::2]):
            item = ProxiesItem()
            item['proxy'] = f'{ip}:{port}'
            yield item
