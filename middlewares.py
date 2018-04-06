# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from datetime import datetime, timedelta
from tz_spider import http_proxy
from tz_spider.http_proxy import ProxyDatabase
from tz_spider.log_config import logger


class TzSpiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class TzSpiderDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ProxyMiddleware:
    # 遇到这些类型的错误直接当做代理不可用处理掉, 不再传给retrymiddleware
    DONT_RETRY_ERRORS = (TimeoutError, ConnectionRefusedError, ValueError)

    def __init__(self):
        # 保存上次不用代理直接连接的时间点
        self.last_no_proxy_time = datetime.now()
        # 一定分钟数后切换回不用代理, 因为用代理影响到速度
        self.recover_interval = 3
        # 是否在超时的情况下禁用代理
        self.invalid_proxy_flag = True
        # 上一次抓新代理的时间
        self.last_fetch_proxy_time = datetime.now()
        # 每隔固定时间强制抓取新代理(min)
        self.fetch_proxy_interval = 240
        # 代理个数阈值，低于这个数量准备抓取新代理
        self.proxies_min_count = 10
        # 在代理未用光的情况下，至少需要隔多少时间抓取
        self.fetch_proxy_timedelta = 60

    def fetch_proxies(self):
        '''
        抓取新代理，耗时较久
        '''
        http_proxy.fetch_check_all()
        proxy = ProxyDatabase()
        proxy.clear()
        proxy.add_items(http_proxy.valid_proxies)
        self.last_fetch_proxy_time = datetime.now()

    def set_proxy(self, request):
        '''
        设置代理
        '''
        proxy = ProxyDatabase()
        count = proxy.get_valid_count()
        if count < self.proxies_min_count:
            self.fetch_proxies()
        if 'proxy' in request.meta.keys():
            invalid_proxy = request.meta['proxy'].split('//')[1]
            logger.info('{} will be set false'.format(invalid_proxy))
            proxy.set_false(invalid_proxy)
            if int(proxy.get_valid_count()) < self.proxies_min_count and datetime.now() > (self.last_no_proxy_time + timedelta(minutes=self.fetch_proxy_timedelta)):
                logger.warning('proxies counts are only {}, start to fetch'.format(proxy.get_valid_count()))
                self.fetch_proxies()
            if int(proxy.get_valid_count()) == 0:
                logger.warning('proxies all invalid, fetch new.')
                self.fetch_proxies()
            request.meta['proxy'] = 'http://' + proxy.get_one()
            logger.info('request proxy change to {}'.format(request.meta['proxy']))
        else:
            request.meta['proxy'] = 'http://' + proxy.get_one()
            logger.info('request proxy change to {}'.format(request.meta['proxy']))

    def process_request(self, request, spider):
        """
        将request设置为使用代理
        """
        # 防止部分代理重定向跳转到莫名其妙的网页，由于check时已经检查过，应该不需要了
        # request.meta["dont_redirect"] = True

        # spider发现parse error, 要求更换代理
        if "change_proxy" in request.meta.keys() and request.meta["change_proxy"]:
            self.set_proxy(request)
            request.meta['change_proxy'] = False
        # 定时切换到不使用代理
        if 'proxy' in request.meta.keys() and datetime.now() > (self.last_no_proxy_time + timedelta(minutes=self.recover_interval)):
            logger.info("After %d minutes later, recover from using proxy" % self.recover_interval)
            del request.meta["proxy"]
            self.last_no_proxy_time = datetime.now()
        '''
        # 定时重抓代理
        if datetime.now() > self.last_fetch_proxy_time + timedelta(minutes=self.fetch_proxy_interval):
            self.fetch_proxies()
        '''

    def process_response(self, request, response, spider):
        """
        检查response.status, 根据status是否在允许的状态码中决定是否切换proxy, 或者禁用proxy
        """
        if response.status != 200:
            if '找不到文件或目录' in response.text:
                return response
            logger.info("response status[%d] not in spider.website_possible_httpstatus_list" % response.status)
            self.set_proxy(request)
            new_request = request.copy()
            new_request.dont_filter = True
            return new_request
        else:
            return response

    def process_exception(self, request, exception, spider):
        """
        处理由于使用代理导致的连接异常
        """
        if isinstance(exception, self.DONT_RETRY_ERRORS):
            self.set_proxy(request)
            new_request = request.copy()
            new_request.dont_filter = True
            return new_request
