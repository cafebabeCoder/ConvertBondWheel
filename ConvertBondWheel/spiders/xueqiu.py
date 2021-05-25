# -*- coding: utf-8 -*-
import json
import requests
import logging
import scrapy
from scrapy.http import Request, FormRequest, HtmlResponse
from ConvertBondWheel.items import XueqiuItem 

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
    allowed_domains = ['xueqiu.com']
    start_urls = ['https://xueqiu.com/cubes/rebalancing/show_origin.json?rb_id=94172067&cube_symbol=ZH2545675']
    custom_settings = {'ITEM_PIPELINES':{'ConvertBondWheel.pipelines.XueqiuPipeline': 300}}
    mycookie = MyCookie().get_my_cookie()

    HEADER = {
        'Host': 'xueqiu.com',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'X-Requested-With': 'XMLHttpRequest',
    }

    # 用cookie模拟登陆部分参考：https://www.cnblogs.com/why957/p/9297779.html 
    # 重写了爬虫类的方法, 实现了自定义请求, 运行成功后会调用callback回调函数
    def start_requests(self):
        yield scrapy.FormRequest(url="https://xueqiu.com/cubes/rebalancing/show_origin.json?rb_id=94172067&cube_symbol=ZH2545675",   # 真正处理request的部分
                        headers=self.HEADER,  # 注意此处的headers
                        cookies=self.mycookie,  #引用登陆的cookie
                        meta={'cookiejar': 1},    # 传递cookie
                        callback=self.parse,
                        dont_filter=True)

    def parse(self, response):
        logging.info(response.body.decode('utf-8'))
        result = json.loads(response.body)
        citems = {}
        rows = result['rebalancing']['rebalancing_histories']
        for row in rows:
            citem = XueqiuItem()
            citem['stock_id'] = row['stock_id']
            citem['stock_name'] = row['stock_name']
            citem['stock_symbol'] = row['stock_symbol']
            citem['target_weight'] = row['target_weight']
            citems[citem['stock_id']] = citem
        yield citems
