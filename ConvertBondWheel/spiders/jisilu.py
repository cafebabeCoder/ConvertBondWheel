# -*- coding: utf-8 -*-
import json
import requests
import scrapy

from ConvertBondWheel.items import ConvertbondwheelItem


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
        # 'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }

    def parse(self, response):
        result = json.loads(response.body)
        rows = result['rows']
        citems = {}
        sess = requests.Session()
        for row in rows:
            citem = ConvertbondwheelItem()
            cellItem = row['cell']
            citem['price'] = cellItem['price']
            citem['premium_rt'] = cellItem['premium_rt']
            citem['value_score'] = self.get_score(citem['price'], citem['premium_rt'])
            citem['bond_id'] = cellItem['bond_id']
            # 加入转股日期
            conver_dt_link = "https://www.jisilu.cn/data/cbnew/detail_pic/?display=premium_rt&bond_id=" + citem['bond_id']
            # yield scrapy.Request(conver_dt_link, callback=self.parse_convert_dt, headers=self.HEADER, meta={'boundid' : citem['bond_id'], 'item' : citem})
            html = sess.get(conver_dt_link, headers=self.HEADER).text

            citem['convert_dt'] = json.loads(html)['convert_dt']
            citem['bond_nm'] = cellItem['bond_nm']
            citem['increase_rt'] = cellItem['increase_rt']
            citem['sprice'] = cellItem['sprice']
            citem['stock_nm'] = cellItem['stock_nm']
            citem['sincrease_rt'] = cellItem['sincrease_rt']
            citem['pb'] = cellItem['pb']
            citem['convert_price'] = cellItem['convert_price']
            citem['convert_value'] = cellItem['convert_value']
            citem['rating_cd'] = cellItem['rating_cd']
            citem['put_convert_price'] = cellItem['put_convert_price']
            citem['force_redeem_price'] = cellItem['force_redeem_price']
            citem['convert_amt_ratio'] = cellItem['convert_amt_ratio']
            citem['short_maturity_dt'] = cellItem['short_maturity_dt']
            citem['year_left'] = cellItem['year_left']
            citem['ytm_rt'] = cellItem['ytm_rt']
            citem['ytm_rt_tax'] = cellItem['ytm_rt_tax']
            citem['volume'] = cellItem['volume']
            if 'EB' in citem['bond_nm'] or citem['volume'] == '0.00':
                continue
            citems[citem['bond_id']] = citem
        yield citems


    def parse_convert_dt(self, response):
        # boundid = response.meta['boundid']
        # item = response.meta['item']
        result = json.loads(response.body)
        convert_dt = result['convert_dt']
        # item['convert_dt'] = convert_dt
        return convert_dt

    def get_score(self, price, premium_rt):
        return float(price) + float(premium_rt.split('%')[0])
