# -*- coding: utf-8 -*-
import scrapy
import json
from ConvertBondWheel.items import ConvertbondwheelItem
import pandas as pd
from ConvertBondWheel.analysis.analysis import Analysis
import datetime

class JisiluSpider(scrapy.Spider):
    name = 'jisilu'
    allowed_domains = ['jisilu.cn']
    start_urls = ['https://www.jisilu.cn/data/cbnew/cb_list/?___jsl=LST___t']

    HEADER = {
        'Host': 'www.jisilu.cn',
        'Connection': 'keep-alive',
        'Cache-Control': 'max - age = 0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Referer': 'https://www.vipmro.com/',
        # 'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }

    def parse(self, response):
        result = json.loads(response.body)
        date = datetime.datetime.now().strftime('%Y%m%d')
        output = "../../data/" + date + ".csv"
        an = Analysis(result, output)
        an.process()
