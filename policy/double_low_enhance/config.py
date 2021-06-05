#!/usr/bin/env python
# -*- coding: utf-8 -*

double_low_conf = {
    'db_topk': 0.1,
    'min_curr_iss_amt': 9,  # <剩余规模
    'volatility': 0.1,  # >波动率
    'premium_rt': 0.2,  # <溢价率
    'min_price': 115,  # <可转债价格
    'min_dblow': 125,  # <双低价格
    'redeem': ['Y'],  #  Y=强赎 不在强赎
    'min_year_left': 1,  # >剩余到期年限 (不要一年内到期的)
    'ytm_rt': -0.01,  # > 到期收益率
    'pluse_out_step':10, # 脉冲轮出时， 轮出债比轮入新债双低值大多少
    'pulse_out_price_median':110, # 脉冲轮出时， 市场价格中位数
    'pulse_out_price':[120, 125], # 脉冲轮出时< 110 和>110 对应的轮出价格
    'pulse_out_dblow':[125, 130],  #同上， 双低值
    'user_zh_columns':[u'转债名称', u'双低', u'现价', u'溢价率', u'剩余规模', u'波动率', u'涨跌幅', u'成交额(万元)', u'换手率'],

}