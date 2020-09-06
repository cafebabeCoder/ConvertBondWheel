# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import datetime
import os
import pandas as pd
import tushare as ts
from ConvertBondWheel.settings import OUTPUT, VOL_DATE_AGO, MIN_VOL, TOKEN


class ConvertbondwheelPipeline(object):
    # 写入file ,指定path
    def __init__(self):
        self.dict = {
            'value_score': '得分',
            'bond_id': '代码',
            'bond_nm': '转债名称',
            'price': '现价',
            'increase_rt': '涨跌幅',
            'stock_nm': '正股名称',
            'sprice': '正股价',
            'sincrease_rt': '正股涨跌',
            'pb': 'PB',
            'convert_price': '转股价',
            'convert_value': '转股价值',
            'premium_rt': '溢价率',
            'rating_cd': '评价',
            'put_convert_price': '回售触发价',
            'force_redeem_price': '强赎触发价',
            'convert_amt_ratio': '转债占比',
            'convert_dt': '转股起始日',
            'short_maturity_dt': '到期时间',
            'year_left': '剩余年限',
            'ytm_rt': '到期税前收益',
            'ytm_rt_tax': '到期税后收益',
            'volume': '成交额(万元)',
            'vol_mean': str(VOL_DATE_AGO) + '天平均成交额(万元)',
        }
        self.columns = ['value_score', 'bond_id', 'bond_nm', 'price', 'increase_rt', 'stock_nm', 'sprice',
                        'sincrease_rt',
                        'pb', 'convert_price', 'convert_value', 'premium_rt', 'rating_cd', 'put_convert_price',
                        'force_redeem_price', 'convert_amt_ratio', 'convert_dt', 'short_maturity_dt', 'year_left', 'ytm_rt',
                        'ytm_rt_tax', 'volume', 'vol_mean']
        self.header = [self.dict[x] for x in self.columns]
        date = datetime.datetime.now().strftime('%Y%m%d')
        if not os.path.exists(OUTPUT):
            os.makedirs(OUTPUT)
        self.output = OUTPUT + date + ".csv"
        print("save to path: ", self.output)
        ts.set_token(TOKEN)
        self.pro = ts.pro_api()
        # self.conn = ts.get_apis()

    def getVolMean(self, code, start_date):
        dfs_sh = self.pro.cb_daily(ts_code=code+".SH", start_date=start_date)
        dfs_sz = self.pro.cb_daily(ts_code=code+".SZ", start_date=start_date)
        dfs = pd.concat([dfs_sh, dfs_sz], axis=0)
        try:
            vol = dfs.loc[:, 'vol'].mean()
        except:
            print("error:" + code)
            vol = 0
        print(vol)
        return vol

    def process_item(self, maps, spider):
        # print(maps)
        citems = []
        for k in maps:
            citems.append(maps[k])
        df = pd.DataFrame(citems)

        #获取历史成交量

        start_date = (datetime.datetime.now() - datetime.timedelta(days=VOL_DATE_AGO)).strftime('%Y%m%d')

        df['vol_mean'] = df['bond_id'].map(lambda x: self.getVolMean(x, start_date)).round(2)
        # df['vol_mean'] = 0
        df = df.drop(df[df.vol_mean < MIN_VOL].index)

        df_sort = df.sort_values('value_score')
        df_sort.to_csv(self.output, index=None, encoding='utf8', columns=self.columns, header=self.header)

        # ts.close_apis(self.conn)

