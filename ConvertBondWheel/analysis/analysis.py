import pandas as pd
from ConvertBondWheel.items import ConvertbondwheelItem
import json
import datetime

class Analysis:
    def __init__(self, jstr, output):
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
            'short_maturity_dt': '到期时间',
            'year_left': '剩余年限',
            'ytm_rt': '到期税前收益',
            'ytm_rt_tax': '到期税后收益',
            'volume': '成交额(万元)',
        }
        self.columns = ['value_score', 'bond_id', 'bond_nm', 'price', 'increase_rt', 'stock_nm', 'sprice',
                        'sincrease_rt',
                        'pb', 'convert_price', 'convert_value', 'premium_rt', 'rating_cd', 'put_convert_price',
                        'force_redeem_price', 'convert_amt_ratio', 'short_maturity_dt', 'year_left', 'ytm_rt',
                        'ytm_rt_tax', 'volume']
        self.header = [self.dict[x] for x in self.columns]
        self.jstr = jstr
        self.output = output

    def process(self):
        rows = self.jstr['rows']
        citems = []
        for row in rows:
            citem = ConvertbondwheelItem()
            cellItem = row['cell']
            citem['price'] = cellItem['price']
            citem['premium_rt'] = cellItem['premium_rt']
            citem['value_score'] = self.get_score(citem['price'], citem['premium_rt'])
            citem['bond_id'] = cellItem['bond_id']
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
            citems.append(citem)
        df = pd.DataFrame(citems)
        df_sort = df.sort_values('value_score')
        df_sort.to_csv(self.output, index=None, encoding='gbk', columns=self.columns, header=self.header)

    def get_score(self, price, premium_rt):
        return float(price) + float(premium_rt.split('%')[0])


if __name__ == "__main__":
    with open("../../data/data", 'rb') as load_f:
        jstr = json.load(load_f)
    date = datetime.datetime.now().strftime('%Y%m%d')
    output = "../../data/" + date + ".csv"
    an = Analysis(jstr, output)
    an.process()