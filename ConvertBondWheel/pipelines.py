# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import datetime
import os
import pandas as pd
from ConvertBondWheel.settings import OUTPUT,FILENAME, VOL_DATE_AGO, MIN_VOL, TOKEN, XUEQIU_FILENAME 
from ConvertBondWheel.fields_config import jisulu_used_columns, jisilu_dict, xueqiu_dict, xueqiu_used_columns


class XueqiuPipeline(object):
    def __init__(self):
        self.columns = xueqiu_used_columns 
        self.header = [xueqiu_dict[x] for x in self.columns]
        if not os.path.exists(OUTPUT):
            os.makedirs(OUTPUT)
        self.output = OUTPUT + XUEQIU_FILENAME + ".csv"
        print("[xueqiu] save to path: ", self.output)

    def process_item(self, maps, spider):
        if spider.name == 'xueqiu':
            citems = []
            if maps is not None:
                for k in maps:
                    citems.append(maps[k])
                df = pd.DataFrame(citems)
                df.to_csv(self.output, index=None, encoding='utf8', columns=self.columns, header=self.header)
     

class ConvertbondwheelPipeline(object):
    # 写入file ,指定path
    def __init__(self):
        self.columns = jisulu_used_columns
        self.header = [jisilu_dict[x] for x in self.columns]
        if not os.path.exists(OUTPUT):
            os.makedirs(OUTPUT)
        self.output = OUTPUT + FILENAME + ".csv"
        print("[jisilu] save to path: ", self.output)

    def process_item(self, maps, spider):
        if spider.name == 'jisilu':
            citems = []
            for k in maps:
                citems.append(maps[k])
            df = pd.DataFrame(citems)
            # dblow str 2 float
            df['dblow'] = df['dblow'].astype(float) 
            df_sort = df.sort_values('dblow')
            # dblow float 2 str
            df_sort['dblow'] = df_sort['dblow'].apply(lambda x: format(x, ".2f"))
    
            #获取历史成交量
            # start_date = (datetime.datetime.now() - datetime.timedelta(days=VOL_DATE_AGO)).strftime('%Y%m%d')
            # df['vol_mean'] = df['bond_id'].map(lambda x: self.getVolMean(x, start_date)).round(2)
            # df = df.drop(df[df.vol_mean < MIN_VOL].index)
    
            df_sort.to_csv(self.output, index=None, encoding='utf8', columns=self.columns, header=self.header)
    
