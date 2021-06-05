# -*- coding: utf-8 -*-
import json
import requests
import logging
import scrapy
from scrapy.http import Request, FormRequest, HtmlResponse

from ConvertBondWheel.items import ConvertbondwheelItem
from ConvertBondWheel.fields_config import jisulu_used_columns


class JisiluSpider(scrapy.Spider):
    name = 'jisilu'
    allowed_domains = ['jisilu.cn']
    start_urls = ['https://www.jisilu.cn/data/cbnew/cb_list/?___jsl=LST___t']
    custom_settings = {'ITEM_PIPELINES':{'ConvertBondWheel.pipelines.ConvertbondwheelPipeline': 300}}
    sess = requests.Session()

    HEADER = {
        'Host': 'www.jisilu.cn',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'X-Requested-With': 'XMLHttpRequest',
    }

    # 模拟登陆部分： https://scrapy-cookbook.readthedocs.io/zh_CN/latest/scrapy-11.html
    # 重写了爬虫类的方法, 实现了自定义请求, 运行成功后会调用callback回调函数
    def start_requests(self):
        yield scrapy.FormRequest(url="https://www.jisilu.cn/account/ajax/login_process/",   # 真正处理request的部分
                        headers=self.HEADER,  # 注意此处的headers
                        meta={'cookiejar': 1},    # 传递cookie
                        formdata={
                            'return_url':'https://www.jisilu.cn/',
                            'user_name': 'cf26d9bff1657788b9f2587308aebd45',
                            'password': '161613817ae74c34bcc7fffa8e4acdfe',
                            'net_auto_login':'1',
                            '_post_type':'ajax',
                            'aes':'1', 
                        },
                        callback=self.after_login,
                        dont_filter=True)

    def after_login(self, response):
        # logging.info(response.body.decode('utf-8'))
        # 登录之后带cookie请求新的页面，这里response没啥用
        for url in self.start_urls:
            logging.info('request url=' + url)
            yield Request(url, 
                        meta={'cookiejar': response.meta['cookiejar']}, #记得带cookie
                        headers=self.HEADER,
                        dont_filter=True,
                        callback=self.parse, )

    def parse(self, response):
        result = json.loads(response.body)
        rows = result['rows']
        citems = {}
        for row in rows:
            citem = ConvertbondwheelItem()
            cellItem = row['cell']
            for column in jisulu_used_columns:
                # 双低值计算, 已经用集思录代替
                # if column == 'value_score':
                #    citem['value_score'] = float(citem['price']) + float(citem['preminum_rt'].split('%')[0])
                if column == 'convert_dt':
                    # 加入转股日期, 不要用scrapy了， 每次写都不对 
                    conver_dt_link = "https://www.jisilu.cn/data/cbnew/detail_pic/?display=premium_rt&bond_id=" + citem['bond_id']
                    html = self.sess.get(conver_dt_link, headers=self.HEADER).text
                    citem['convert_dt'] = json.loads(html)['convert_dt']

                else:
                    citem[column] = cellItem[column]

            if 'EB' in citem['bond_nm'] or citem['volume'] == '0.00':
                continue
            citems[citem['bond_id']] = citem
        yield citems
