import sqlite3
import traceback
import random
from time import sleep
from concurrent import futures
from custom_log import logger

import requests
from lxml import etree

valid_proxies = []


def get_html(url: str):
    '''
    return: lxml对象
    '''
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    html = etree.HTML(r.text)
    return html


def fetch_kuaidaili() ->list:
    '''
    抓取快代理
    '''
    base_url = 'https://www.kuaidaili.com/free/inha/{}/'
    try:
        proxies = []
        for page in range(1, 3):
            url = base_url.format(page)
            html = get_html(url)
            ip = html.xpath('//div[@id="list"]/table/tbody/tr/td[@data-title="IP"]/text()')
            port = html.xpath('//div[@id="list"]/table/tbody/tr/td[@data-title="PORT"]/text()')
            for l, r in zip(ip, port):
                proxies.append('{}:{}'.format(l, r))
            sleep(3)
    except Exception as e:
        logger.exception('error')
        traceback.print_exc()
        proxies = []
    if not proxies:
        logger.warning(' fail to fetch kuaidaili')
    return proxies


def fetch_xici() ->list:
    '''
    抓取xici代理
    '''
    base_url = 'http://www.xicidaili.com/nn/{}'
    try:
        proxies = []
        for page in range(1, 3):
            url = base_url.format(page)
            html = get_html(url)
            ip = html.xpath('//tr[@class="odd"]/td[2]/text()')
            port = html.xpath('//tr[@class="odd"]/td[3]/text()')
            for l, r in zip(ip, port):
                proxies.append('{}:{}'.format(l, r))
    except Exception as e:
        logger.exception('error')
        traceback.print_exc()
        proxies = []
    if not proxies:
        logger.warning(' fail to fetch xici')
    return proxies


def fetch_mimvp() ->list:
    '''
    抓取mimvp代理
    '''
    url = 'https://proxy.mimvp.com/free.php?proxy=in_hp'
    try:
        html = get_html(url)
        ip = html.xpath('//div[@class="free-list"]/table/tbody/td[@class="tbl-proxy-ip"]/text()')
        port = [80 for i in ip]
        proxies = []
        for l, r in zip(ip, port):
            proxies.append('{}:{}'.format(l, r))
    except Exception as e:
        logger.exception('error')
        traceback.print_exc()
        proxies = []
    if not proxies:
        logger.warning(' fail to fetch mimvp')
    return proxies


def fetch_66ip() ->list:
    '''
    抓取66ip代理
    '''
    url = 'http://www.66ip.cn/nmtq.php?getnum=512&isp=0&anonymoustype=0&start=&ports=&export=&ipaddress=&area=0&proxytype=2&api=66ip'
    try:
        html = get_html(url)
        ip_port = html.xpath('string(//body)').split('\r\n\t\t')[1:-2]
        proxies = []
        for i in ip_port:
            proxies.append(i)
    except Exception as e:
        logger.exception('error')
        traceback.print_exc()
        proxies = []
    if not proxies:
        logger.warning(' fail to fetch 66ip')
    return proxies


def fetch_3366ip() ->list:
    '''
    抓取3366ip代理
    '''
    base_url = 'http://www.ip3366.net/free/?stype=1&page={}'
    try:
        proxies = []
        for page in range(1, 4):
            url = base_url.format(page)
            html = get_html(url)
            tmp = [i.text for i in html.xpath('//tbody/tr/td')]
            res = [i for i in tmp if i.isdigit() or ''.join(i.split('.')).isdigit()]
            ip = [i for l, i in enumerate(res) if l % 2 == 0]
            port = [i for l, i in enumerate(res) if l % 2 == 1]
            for l, r in zip(ip, port):
                proxies.append('{}:{}'.format(l, r))
    except Exception as e:
        logger.exception('error')
        traceback.print_exc()
        proxies = []
    if not proxies:
        logger.warning(' fail to fetch 3366ip')
    return proxies


def fetch_mimiip() ->list:
    '''
    抓取mimiip代理
    '''
    base_url = 'http://www.mimiip.com/gngao/{}'
    try:
        proxies = []
        for page in range(1, 4):
            url = base_url.format(page)
            html = get_html(url)
            tmp = [i.text for i in html.xpath('//table/tr/td')]
            res = [i for i in tmp if i.isdigit() or ''.join(i.split('.')).isdigit()]
            ip = [i for l, i in enumerate(res) if l % 2 == 0]
            port = [i for l, i in enumerate(res) if l % 2 == 1]
            for l, r in zip(ip, port):
                proxies.append('{}:{}'.format(l, r))
    except Exception as e:
        logger.exception('error')
        traceback.print_exc()
        proxies = []
    if not proxies:
        logger.warning(' fail to fetch mimiip')
    return proxies


def fetch_data5u() ->list:
    '''
    抓取data5u代理
    '''
    url = 'http://www.data5u.com/free/gngn/index.shtml'
    try:
        html = get_html(url)
        tmp = [i.text for i in html.xpath('//ul[@class="l2"]/span/li')]
        res = [i for i in tmp if i and (i.isdigit() or ''.join(i.split('.')).isdigit())]
        ip = [i for l, i in enumerate(res) if l % 2 == 0]
        port = [i for l, i in enumerate(res) if l % 2 == 1]
        proxies = []
        for l, r in zip(ip, port):
            proxies.append('{}:{}'.format(l, r))
    except Exception as e:
        logger.exception('error')
        traceback.print_exc()
        proxies = []
    if not proxies:
        logger.warning(' fail to fetch data5u')
    return proxies


def fetch_ip181() ->list:
    '''
    抓取ip181代理
    '''
    url = 'http://www.ip181.com/'
    try:
        html = get_html(url)
        tmp = [i.text for i in html.xpath('//tbody/tr/td')]
        res = [i for i in tmp if i and (i.isdigit() or ''.join(i.split('.')).isdigit())]
        ip = [i for l, i in enumerate(res) if l % 2 == 0]
        port = [i for l, i in enumerate(res) if l % 2 == 1]
        proxies = []
        for l, r in zip(ip, port):
            proxies.append('{}:{}'.format(l, r))
    except Exception as e:
        logger.exception('error')
        traceback.print_exc()
        proxies = []
    if not proxies:
        logger.warning(' fail to fetch ip181')
    return proxies


def fetch_kxdaili() ->list:
    '''
    抓取kaixin代理
    '''
    base_url = 'http://www.kxdaili.com/dailiip/1/{}.html#ip'
    try:
        proxies = []
        for page in range(1, 4):
            url = base_url.format(page)
            html = get_html(url)
            tmp = [i.text for i in html.xpath('//tbody/tr/td')]
            res = [i for i in tmp if i and (i.isdigit() or ''.join(i.split('.')).isdigit())]
            ip = [i for l, i in enumerate(res) if l % 2 == 0]
            port = [i for l, i in enumerate(res) if l % 2 == 1]
            for l, r in zip(ip, port):
                proxies.append('{}:{}'.format(l, r))
    except Exception as e:
        logger.exception('error')
        traceback.print_exc()
        proxies = []
    if not proxies:
        logger.warning(' fail to fetch kxdaili')
    return proxies


def check(proxy: str):
    '''
    检测代理能否正常使用
    '''
    url = "http://httpbin.org/get"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
    proxies = {}
    proxies['http'] = 'http://' + proxy
    proxies['https'] = 'https://' + proxy
    try:
        # logger.info('verify {} ...'.format(proxy))
        resp = requests.get(url, headers=headers, proxies=proxies, timeout=12)
        if resp.status_code == 200:
            r = resp.json()
            if r['url'] == url:
                valid_proxies.append(proxy)
                logger.info('{} useful'.format(proxy))
    except Exception as e:
        pass


def fetch_check_all():
    '''
    抓取并把所有代理通过check()检测是否可用
    '''
    proxies = fetch_kuaidaili()
    proxies.extend(fetch_mimvp())
    proxies.extend(fetch_xici())
    proxies.extend(fetch_kxdaili())
    proxies.extend(fetch_mimiip())
    proxies.extend(fetch_3366ip())
    proxies.extend(fetch_66ip())
    proxies.extend(fetch_data5u())
    proxies.extend(fetch_ip181())

    p = ProxyDatabase()
    db_proxies = p.get_valid_items()
    db_invalid_proxies = p.get_invalid_items()
    if db_invalid_proxies:
        no_invalid = set(proxies) - set(db_invalid_proxies)
        proxies = list(no_invalid | set(db_proxies))
    else:
        proxies = list(set(proxies) | set(db_proxies))

    logger.info(proxies)
    workers = min(16, len(proxies))
    with futures.ThreadPoolExecutor(workers) as e:
        e.map(check, proxies)


class ProxyDatabase:
    def __init__(self):
        '''
        初始化数据库连接和游标，创建表proxies：IP_PORT和valid，2个字段
        '''
        self.conn = sqlite3.connect('proxy.db')
        self.cur = self.conn.cursor()
        self.db_name = 'proxies'
        try:
            sql = "CREATE TABLE IF NOT EXISTS {} (id int PRIMARY KEY, IP_PORT varchar(20) NOT NULL, valid int(1) NOT NULL)"
            self.cur.execute(sql.format(self.db_name))
        except Exception as e:
            self.conn.rollback()
            logger.exception('init fail')
            traceback.print_exc()

    def get_one(self) ->str:
        '''
        从表中随机抽取1个proxy
        return like: 127.0.0.1: 8080
        '''
        try:
            sql = "SELECT IP_PORT FROM %s where valid=1"
            self.cur.execute(sql % self.db_name)
            ports = [i[0] for i in self.cur]
        except Exception as e:
            self.conn.rollback()
            logger.exception('get_one fail')
            traceback.print_exc()
        return random.choice(ports)

    def get_valid_items(self) ->list:
        '''
        从表中抽取所有有效的proxies
        '''
        try:
            sql = "SELECT IP_PORT FROM %s where valid=1"
            self.cur.execute(sql % self.db_name)
            ports = [i[0] for i in self.cur]
        except Exception as e:
            logger.exception('get_all fail')
            traceback.print_exc()
        return ports

    def get_invalid_items(self) ->list:
        '''
        从表中抽取所有无效的proxies
        '''
        try:
            sql = 'SELECT IP_PORT FROM %s where valid=0'
            self.cur.execute(sql % self.db_name)
            ports = [i[0] for i in self.cur]
        except Exception as e:
            logger.exception('get invalid items fail')
            traceback.print_exc()
        return ports

    def get_all(self) ->list:
        '''
        从表中抽取所有proxies
        '''
        try:
            sql = 'SELECT IP_PORT FROM %s'
            self.cur.execute(sql % self.db_name)
            ports = [i[0] for i in self.cur]
        except Exception as e:
            logger.exception('get all fail')
            traceback.print_exc()
        return ports

    def get_valid_count(self):
        '''
        获取表中有效代理总数
        '''
        try:
            sql = "SELECT COUNT(*) FROM %s where valid=1"
            self.cur.execute(sql % self.db_name)
            count = self.cur.fetchone()[0]
        except Exception as e:
            self.conn.rollback()
            logger.exception('get_count fail')
            traceback.print_exc()
        return count

    def set_false(self, item: str):
        '''
        删除表中对应的proxy
        '''
        try:
            sql = "UPDATE FROM %s SET valid=0 WHERE IP_PORT=%s"
            self.cur.execute(sql % (self.db_name, item))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.exception('set false fail')
            traceback.print_exc()

    def add_one(self, item: str):
        '''
        向表中添加1个proxy
        '''
        try:
            sql = "INSERT INTO %s (IP_PORT, valid) VALUES ('%s', 1)"
            self.cur.execute(sql % (self.db_name, item))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.exception('add fail')
            traceback.print_exc()

    def add_items(self, item: list):
        '''
        向表中添加多个proxies
        '''
        try:
            sql = "INSERT INTO %s (IP_PORT, valid) VALUES ('%s', 1)"
            for i in item:
                logger.info(sql % (self.db_name, i))
                self.cur.execute(sql % (self.db_name, i))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.warning('add_items  fail')
            traceback.print_exc()

    def clear(self):
        '''
        清除表中所有无用proxies
        '''
        try:
            sql = "DELETE FROM %s WHERE valid=0"
            self.cur.execute(sql % self.db_name)
            self.conn.commit()
        except Exception as e:
            logger.warning('clear  fail')
            traceback.print_exc()

    def close(self):
        '''
        关闭游标和数据库连接
        '''
        self.cur.close()
        self.conn.close()


def main():
    proxy = ProxyDatabase()
    old_ip = proxy.get_valid_items()
    length = len(old_ip)
    while length < 12:
        fetch_check_all()
        logger.info(valid_proxies)
        proxy.clear()
        proxy.add_items(valid_proxies)
        length = len(proxy.get_valid_count())
    logger.info(proxy.get_valid_count())
    logger.info(proxy.get_one())


if __name__ == "__main__":
    main()
