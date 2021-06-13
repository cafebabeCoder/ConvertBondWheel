# -*- coding: utf-8 -*-
import json
import requests
import logging
import scrapy
from scrapy.http import Request, FormRequest, HtmlResponse
from ConvertBondWheel.items import XueqiuItem 
from ConvertBondWheel.fields_config import xueqiu_used_columns 

class MyCookie:
    # 用账号登陆, 然后 取出network->cookie 的kv，记下来
    def __init__(self) :
        self.cookie = {}
        with open("/root/workSpace/investProject/ConvertBondWheel/ConvertBondWheel/mycookie", 'r', encoding='utf8') as f:
            lines = f.readlines()
            for line in lines:
                key = line.split("=")[0].strip()
                val = line.split("=")[1].strip()
                self.cookie[key] = val
    def get_my_cookie(self):
        return self.cookie
    

class XueqiuSpider(scrapy.Spider):
    name = 'xueqiu'
    allowed_domains = ['tc.xueqiu.com', 'xueqiu.com']
    custom_settings = {'ITEM_PIPELINES':{'ConvertBondWheel.pipelines.XueqiuPipeline': 300}}
    mycookie = MyCookie().get_my_cookie()

    HEADER = {
        'Host': 'xueqiu.com',
        'Connection': 'keep-alive',
        'cache-control': 'max-age=0',
        'upgrade-insecure-requests': '1',
        'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        # 'X-Requested-With': 'XMLHttpRequest',
        # 'gid': '3041472606811025',
        # ':authority': 'tc.xueqiu.com',
        # ':method': 'GET',
        # ':path': '/tc/snowx/MONI/performances.json?gid=3041472606811025',
        # ':scheme': 'https',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"', 
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
    }

    # 用cookie模拟登陆部分参考：https://www.cnblogs.com/why957/p/9297779.html 
    # 重写了爬虫类的方法, 实现了自定义请求, 运行成功后会调用callback回调函数
    def start_requests(self):
        yield scrapy.Request(url="https://xueqiu.com/P/ZH2545675",   # 真正处理request的部分
                        headers=self.HEADER,  # 注意此处的headers
                        # formdata ={'gid': '3041472606811025'},
                        # method='GET',
                        # cookies=self.mycookie,  #引用登陆的cookie
                        # meta={'cookiejar': 1},    # 传递cookie
                        callback=self.parse,
                        dont_filter=True)

    def parse(self, response):
        # logging.info(response.request.headers)
        # logging.info(response.headers)
        # logging.info(response.body.decode('utf8'))
        resp = response.body.decode('utf8')
        result = ''
        for line in resp.split("\n"):
            if 'SNB.cubeInfo' in line:
                result = line.replace("SNB.cubeInfo = ", '').strip(';')
                logging.debug(result)
        if len(result) < 10:
            logging.error(" Empty!")
            return
        result = json.loads(result)
        citems = {}
        if result['name'] != 'convert_bound':
            logging.error('Result error!')
            return
        holdings = result['view_rebalancing']['holdings'] 
        for holding in holdings:
            citem = XueqiuItem()
            for colum in xueqiu_used_columns:
                citem[colum] = holding[colum]
            citems[citem['stock_symbol']] = citem
        yield citems
