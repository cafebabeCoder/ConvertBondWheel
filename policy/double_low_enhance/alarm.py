import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
print(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import pandas as pd
import json
import datetime
import pandas
import pandas as pd
import tushare as ts
from datetime import timedelta
from ConvertBondWheel.fields_config import xueqiu_used_columns, xueqiu_dict, jisilu_dict, jisulu_used_columns
from config import double_low_conf 

def getTopkDoubleLowPriceMedian(df):
    per = int(df.index.size*double_low_conf['db_topk'])
    return df.sort_values('dblow', ascending=True)[:per]['price'].median()

def getAllBoindPriceMedian(df):
    return df['price'].median()

def periodTake(row, topkDoubleLowPriceMedian, allBoindPriceMedian, conf):
    return row['curr_iss_amt'] < conf['min_curr_iss_amt']  and \
    row['volatility_rate'] > conf['volatility'] and \
    row['premium_rt'] < conf['premium_rt'] and \
    row['price'] < topkDoubleLowPriceMedian and \
    row['price'] < allBoindPriceMedian and \
    row['price'] < conf['min_price'] and \
    row['dblow'] < conf['min_dblow'] and \
    row['redeem_flag'] not in conf['redeem'] and \
    row['ytm_rt'] > conf['ytm_rt'] and \
    row['year_left'] > conf['min_year_left']


def periodOut():
    pass

def pulseTake():
    pass

def pulseOut():
    pass


def per2float(s):
    s = s.strip('%')
    if s!='-':
        return float(s)
    else:
        return -1

def read_data():
    bound_file = '/root/workSpace/investProject/ConvertBondWheel/data/jisiluConvertBound_pre.csv'
    bound = pd.read_csv(bound_file)
    # 替换表头 
    bound_en2ch_col = dict(zip(jisilu_dict.values(), jisilu_dict.keys()))
    bound = bound.rename(columns=bound_en2ch_col) 
    # 处理百分号
    for col in ['increase_rt', 'sincrease_rt', 'premium_rt', 'convert_amt_ratio', 'ytm_rt', 'ytm_rt_tax']:
        bound[col] = bound[col].map(lambda s: per2float(s))
    # for col in ['volatility_rate']:
        # bound[col] = bound[col]/100
    # print(bound)
    return bound

def wheelMethod(bound, double_low_conf):
    # 策略
    # 轮入
    topkDoubleLowPriceMedian = getTopkDoubleLowPriceMedian(bound)
    allBoindPriceMedian = getAllBoindPriceMedian(bound)
    filtered_bound = bound[bound.apply(lambda row : periodTake(row, topkDoubleLowPriceMedian, allBoindPriceMedian, double_low_conf), axis=1)]
    return filtered_bound 

def display(df, user_zh_columns=None, output=None):
    columns = df.columns
    header_bef = [jisilu_dict[x] for x in columns]
    dis_df = df.rename(columns = jisilu_dict)  #换成中文header

    header = user_zh_columns + [col for col in header_bef if col not in user_zh_columns]  # 添加header的顺序
    for col in [u'涨跌幅', u'正股涨跌', u'溢价率', u'转债占比', u'到期税前收益', u'到期税后收益', u'波动率', u'换手率']:
        dis_df[col] = dis_df[col].apply(lambda x: format(x/100, ".2%"))
    # save
    if output is not None:
        dis_df.to_csv(output, index=None, encoding='utf8', columns=header, float_format='%.5f')
    return dis_df.loc[:, header]



def main():
    bound = read_data()
    filtered_bound = wheelMethod(bound, double_low_conf)
    result = display(filtered_bound)
    print(result)

    # balancing_file = '/root/workSpace/investProject/ConvertBondWheel/data/xueqiuRebalancing.csv'
    # balance = pd.read_csv(balancing_file)
    # balance_en2ch_col = dict(zip(xueqiu_dict.values(), xueqiu_dict.keys()))
    # balance = balance.rename(columns=balance_en2ch_col)
    # print(balance)
    # an = Analysis(jstr, output)
    # an.process()

if __name__ == "__main__":
    main()

