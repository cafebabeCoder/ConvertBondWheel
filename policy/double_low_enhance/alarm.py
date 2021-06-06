import sys
from os import path
from numpy.lib.function_base import disp
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
print(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
import pandas as pd
import logging
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
import time
from config import double_low_conf 
from ConvertBondWheel.fields_config import xueqiu_used_columns, xueqiu_dict, jisilu_dict, jisulu_used_columns
from policy.common.utils import  sendEmail
logging.basicConfig(level=logging.DEBUG)


# 仓位管理 
def balance_manege(count):
    if count < 100:
        return 5
    elif count < 200:
        return 10
    elif count< 300:
        return 15
    elif count <400:
        return 20
    else:
        return 25

def toHTML(data, ins, outs, balance_line):
    ori_html = data.to_html()

    #set table style
    ori_html = ori_html.replace("<table", '<table style="border-collapse: collapse;"')

    # set color
    red = ' style="color:red;"'  # in
    green = ' style="color:green;"' # out

    for id in outs:
        id = "*" + id 
        st = "<td>%s</td>" % id
        replace_st = "<td%s>%s</td>" %(red, id)
        ori_html = ori_html.replace(st, replace_st)
    for id in ins:
        id = id
        st = "<td>%s</td>" % id
        replace_st = "<td%s>%s</td>" %(green, id)
        ori_html = ori_html.replace(st, replace_st)

    for id in data.loc[:, u'转债名称']:
        if "*" in id:
            replace_st = "<b>%s<b>" %id
            ori_html = ori_html.replace(str(id), replace_st)

    # set topk
    st = '<th>%d</th>' %balance_line
    replace_st = '<td></td></tr><tr><th>%d</th>' %balance_line
    ori_html = ori_html.replace(st, replace_st)

    return ori_html

# df中双低值排名topk的可转债价格中位数
def getTopkDoubleLowPriceMedian(df):
    per = int(df.index.size*double_low_conf['db_topk'])
    return df.sort_values('dblow', ascending=True)[:per]['price'].median()

# df中价格中位数
def getAllBoundPriceMedian(df):
    return df['price'].median()

# 周期轮入
def periodTake(row, topkDoubleLowPriceMedian, allBoundPriceMedian, conf):
    return row['curr_iss_amt'] < conf['min_curr_iss_amt']  and \
    row['volatility_rate'] > conf['volatility'] and \
    row['premium_rt'] < conf['premium_rt'] and \
    row['price'] < topkDoubleLowPriceMedian and \
    row['price'] < allBoundPriceMedian and \
    row['price'] < conf['min_price'] and \
    row['dblow'] < conf['min_dblow'] and \
    row['redeem_flag'] not in conf['redeem'] and \
    row['ytm_rt'] > conf['ytm_rt'] and \
    row['year_left'] > conf['min_year_left']

# 周期轮出
def periodOut():
    pass

# 脉冲轮入
def pulseTake(row, topkDoubleLowPriceMedian, allBoundPriceMedian, conf, max_out):
    # 轮出债需要比轮入新标的大一定的阈值
    return periodTake(row, topkDoubleLowPriceMedian, allBoundPriceMedian, conf) and \
        max_out - row['dblow'] >= double_low_conf['pulse_out_step']

# 脉冲轮出 此时只是判断有没有满足轮出的可转债
def pulseOut(row, allBoundPriceMedian, conf):
    if allBoundPriceMedian <= conf['pulse_out_price_median']:
        return row['price'] > conf['pulse_out_price'][0] and \
            row['dblow'] > conf['pulse_out_dblow'][0]
    else:
        return row['price'] > conf['pulse_out_price'][1] and \
            row['dblow'] > conf['pulse_out_dblow'][1]

def per2float(s):
    s = s.strip('%')
    if s!='-':
        return float(s) / 100 
    else:
        return -1

# 读市场数据
def read_data(bond_file = '/root/workSpace/investProject/ConvertBondWheel/data/jisiluConvertBound_pre.csv'):
    bond = pd.read_csv(bond_file)
    # 替换表头为英文
    bond_en2ch_col = dict(zip(jisilu_dict.values(), jisilu_dict.keys()))
    bond = bond.rename(columns=bond_en2ch_col) 
    # 处理百分号
    for col in ['increase_rt', 'sincrease_rt', 'premium_rt', 'convert_amt_ratio', 'ytm_rt', 'ytm_rt_tax']:
        bond[col] = bond[col].map(lambda s: per2float(s))
    # for col in ['volatility_rate']:
        # bond[col] = bond[col]/100
    return bond

# 读持仓, 返回持仓名字列表
def read_balancing(balancing_file = '/root/workSpace/investProject/ConvertBondWheel/data/xueqiuRebalancing.csv'):
    balance = pd.read_csv(balancing_file)
    ch2en_col = dict(zip(xueqiu_dict.values(), xueqiu_dict.keys()))
    balance = balance.rename(columns=ch2en_col)
    balance_names = list(balance['stock_name'])
    return balance_names 

# 周期 轮动, 返回可转债名字列表
def periodWheel(bond, double_low_conf):
    # 轮入
    topkDoubleLowPriceMedian = getTopkDoubleLowPriceMedian(bond)
    allBoundPriceMedian = getAllBoundPriceMedian(bond)
    filtered_bond = bond[bond.apply(lambda row : periodTake(row, topkDoubleLowPriceMedian, allBoundPriceMedian, double_low_conf), axis=1)]
    return list(filtered_bond['bond_nm']), []

# 脉冲 轮动, 返回 in out可转债名字列表
def pulseWheel(bond, balance_names, double_low_conf):
    allBoundPriceMedian = getAllBoundPriceMedian(bond) # 所有转债价格中位数
    balance_bond = bond[bond['bond_nm'].apply(lambda x : x in balance_names)] # 轮出债必须在持仓
    out_bond = balance_bond[balance_bond.apply(lambda row : pulseOut(row, allBoundPriceMedian, double_low_conf), axis=1)] # 检查有没有轮出
    # 如果有满足条件的轮出， 检查轮入是否满足条件
    if out_bond.index.size > 0 :
        # 获取轮入标的
        topkDoubleLowPriceMedian = getTopkDoubleLowPriceMedian(bond)
        max_out = out_bond['dblow'].max() # 轮出的可转债双低值
        in_bond = bond[bond.apply(lambda row : pulseTake(row, topkDoubleLowPriceMedian, allBoundPriceMedian, double_low_conf, max_out), axis=1)]
        if in_bond.empty:
            return [], list(out_bond['bond_nm'])
        else:
            return list(in_bond['bond_nm']), list(out_bond['bond_nm'])
    else:
        return [],[] 

# 在持仓中， 显示加*号
def star_balance(s, balance_names):
    if s in balance_names: 
        return '*'+s
    else:
        return s

def unstar_balance(s):
    return s.replace("*", "")

# 仅用于展示 和 保存
def to_display(bond, balance_names, in_names, out_names, user_zh_columns):
    # 持仓的股票 加 *
    bond['bond_nm'] = bond['bond_nm'].apply(lambda s: star_balance(s, balance_names))

    # 仅显示持仓+轮入+轮出
    display_rows = balance_names + in_names + out_names
    bond = bond[bond['bond_nm'].apply(lambda s: unstar_balance(s) in display_rows)]

    # 换成中文header
    header_ch = [jisilu_dict[x] for x in bond.columns] # 中文header
    bond = bond.rename(columns = jisilu_dict) 

    # 显示百分号
    for col in [u'涨跌幅', u'正股涨跌', u'溢价率', u'转债占比', u'到期税前收益', u'到期税后收益', u'波动率', u'换手率']:
        bond[col] = bond[col].apply(lambda x: format(x, ".2%"))

    # 指定优先显示的列&列的顺序
    header = user_zh_columns + [col for col in header_ch if col not in user_zh_columns]  # 添加header的顺序

    return bond.loc[:, header]

# to_html & save
def to_alarm(bond, in_names, out_names, balance_line, output=None, send_email=False):
    if output:

        ori_html = toHTML(bond, in_names, out_names, balance_line)
        with open(output, 'w', encoding='utf8') as f:
            f.write(ori_html)
            f.close()
    
    if send_email:
        msg = MIMEText(ori_html, 'html', 'utf-8')
        sendEmail(msg, '可转债脉冲轮动', '可转债脉冲轮动')

def main(argv):
    logging.info("[%s start!]" %" ".join(argv)) 
    policy = argv[1]  # policy = ['period', 'pulse']
    bond = read_data()  #读市场
    logging.debug("Read bound data:")
    logging.debug(bond)
    balance_names = read_balancing()  #读持仓
    logging.debug("Read current banlance: %s\n" %','.join(balance_names))
    if policy == 'period':
        in_names, out_names = periodWheel(bond, double_low_conf)
        result = to_display(bond, balance_names, in_names, out_names, user_zh_columns=double_low_conf['user_zh_columns'])
        logging.debug(result)
    elif policy == 'pulse':
        pulse_path = '/root/workSpace/investProject/ConvertBondWheel/data/pulse_alarm.html'
        in_names, out_names = pulseWheel(bond, balance_names, double_low_conf)
        logging.debug("Bond Wheel: in=%d\tout=%d\nin:%s\nout:%s" %(len(in_names), len(out_names), ', '.join(in_names), ', '.join(out_names)))
        if len(out_names) > 0:
            result = to_display(bond, balance_names, in_names, out_names, user_zh_columns=double_low_conf['user_zh_columns'])
            logging.debug("Display:")
            balance_line = balance_manege(bond.index.size)
            to_alarm(result, in_names, out_names, balance_line, output=pulse_path, send_email=True)
            logging.debug(result)
    else:
        logging.error("Parameter policy error!!")


if __name__ == "__main__":
    main(sys.argv)

