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

}