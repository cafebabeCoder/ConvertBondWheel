#!/usr/bin/env python
# -*- coding: utf-8 -*
from ConvertBondWheel.settings import OUTPUT,FILENAME, VOL_DATE_AGO, MIN_VOL, TOKEN, XUEQIU_FILENAME 

# 定义jisilu的字段
jisilu_dict = {
    # 'value_score': '得分',
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
    'volatility_rate': '波动率',
    'dblow': '双低',
    'curr_iss_amt': '剩余规模',
    'redeem_flag':'强赎公告',
    'turnover_rt':'换手率',
    # 'vol_mean': str(VOL_DATE_AGO) + '天平均成交额(万元)',
    # 双低 现价 溢价率 剩余规模 波动率 涨跌幅 成交额(万元) 换手率
    # increase_rt,sincrease_rt, premium_rt, convert_amt_ratio,  
    # 涨跌幅, 正股涨跌, 溢价率, 转债占比, 到期税前收益, 到期税后收益, 波动率, 换手率 

}
jisulu_used_columns = ['dblow', 'bond_id', 'bond_nm', 'price', 'increase_rt', 'stock_nm', 'sprice', 'sincrease_rt',
                        'pb', 'convert_price', 'convert_value', 'premium_rt', 'rating_cd', 'put_convert_price',
                        'force_redeem_price', 'convert_amt_ratio', 'convert_dt', 'short_maturity_dt', 'year_left', 'ytm_rt',
                        'ytm_rt_tax', 'volume', 'volatility_rate', 'curr_iss_amt','redeem_flag','turnover_rt']

# 定义雪球需要的字段
xueqiu_dict = {
    'stock_name': '股票名称',
    'stock_symbol': '股票代码',
    'weight': '持仓',
}
xueqiu_used_columns = ['stock_name', 'stock_symbol', 'weight']