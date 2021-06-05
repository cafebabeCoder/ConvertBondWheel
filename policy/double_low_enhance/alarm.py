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
logging.basicConfig(level=logging.INFO)

def timeStr():
    t = time.strftime(str("%Y-%m-%d %H:%M:%S"), time.localtime())
    s = '[%s]' % t
    return s

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

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

def sendEmail(content, add, title):

    # send email
    from_addr = 'luoyu091@163.com'
    password = 'ZIVRTJYTZTGODWUX'
    to_addr = ['381336925@qq.com', 'moonwalkings@vip.qq.com']
    # to_addr = ['381336925@qq.com']
    smtp_server = 'smtp.163.com'
    stime = timeStr()  

    msg = MIMEText(content, 'html', 'utf-8')
    msg['From'] = _format_addr('%s <%s>' % (add, from_addr))
    # msg['To'] = _format_addr('test <%s>' % ",".join(to_addr))
    msg['To'] = ",".join(to_addr) 
    msg['Subject'] = Header('%s %s' % (title, stime), 'utf-8').encode()

    server = smtplib.SMTP_SSL(smtp_server, 465)
    # server.set_debuglevel(1)
    server.ehlo(smtp_server)
    server.login(from_addr, password)
    server.sendmail(from_addr, to_addr, msg.as_string())
    server.quit()


def toHTML(data, ins, outs, top_k):
    ori_html = data.to_html()

    #set table style
    ori_html = ori_html.replace("<table", '<table style="border-collapse: collapse;"')

    # set color
    red = ' style="color:red;"'  # in
    green = ' style="color:green;"' # out

    for id in outs:
        st = "<td>%s</td>" % id
        replace_st = "<td%s>%s</td>" %(red, id)
        ori_html = ori_html.replace(st, replace_st)
    for id in ins:
        st = "<td>%s</td>" % id
        replace_st = "<td%s>%s</td>" %(green, id)
        ori_html = ori_html.replace(st, replace_st)

    for id in data.iloc[:, 2]:
        if "*" in id:
            replace_st = "<b>%s<b>" %id
            ori_html = ori_html.replace(str(id), replace_st)

    # set topk
    st = '<th>%d</th>' %top_k
    replace_st = '<td></td></tr><tr><th>%d</th>' %top_k
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
        max_out - row['price'] >= double_low_conf['pulse_out_step']

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
        return float(s)
    else:
        return -1

# 读市场数据
def read_data(bound_file = '/root/workSpace/investProject/ConvertBondWheel/data/jisiluConvertBound_pre.csv'):
    bound = pd.read_csv(bound_file)
    # 替换表头为英文
    bound_en2ch_col = dict(zip(jisilu_dict.values(), jisilu_dict.keys()))
    bound = bound.rename(columns=bound_en2ch_col) 
    # 处理百分号
    for col in ['increase_rt', 'sincrease_rt', 'premium_rt', 'convert_amt_ratio', 'ytm_rt', 'ytm_rt_tax']:
        bound[col] = bound[col].map(lambda s: per2float(s))
    # for col in ['volatility_rate']:
        # bound[col] = bound[col]/100
    logging.debug(bound)
    return bound

# 读持仓
def read_balancing(balancing_file = '/root/workSpace/investProject/ConvertBondWheel/data/xueqiuRebalancing.csv'):
    balance = pd.read_csv(balancing_file)
    balance_en2ch_col = dict(zip(xueqiu_dict.values(), xueqiu_dict.keys()))
    balance = balance.rename(columns=balance_en2ch_col)
    return balance

# 周期 轮动
def periodWheel(bound, double_low_conf):
    # 轮入
    topkDoubleLowPriceMedian = getTopkDoubleLowPriceMedian(bound)
    allBoundPriceMedian = getAllBoundPriceMedian(bound)
    filtered_bound = bound[bound.apply(lambda row : periodTake(row, topkDoubleLowPriceMedian, allBoundPriceMedian, double_low_conf), axis=1)]
    return filtered_bound 

# 脉冲 轮动
def pulseWheel(bound, balance, double_low_conf):
    allBoundPriceMedian = getAllBoundPriceMedian(bound) # 所有转债价格中位数
    balance_ids = list(balance['stock_name'])  # 持仓转债名称
    balance_bound = bound[bound['bond_nm'].apply(lambda x : x in balance_ids)] # 轮出债必须在持仓
    out_bound = balance_bound[balance_bound.apply(lambda row : pulseOut(row, allBoundPriceMedian, double_low_conf), axis=1)] # 检查有没有轮出
    # 如果有满足条件的轮出， 检查轮入是否满足条件
    if out_bound.index.size > 0 :
        # 获取轮入标的
        topkDoubleLowPriceMedian = getTopkDoubleLowPriceMedian(bound)
        logging.debug(out_bound)
        max_out = out_bound['dblow'].max() # 轮出的可转债双低值
        in_all_bound = bound[bound.apply(lambda row : pulseTake(row, topkDoubleLowPriceMedian, allBoundPriceMedian, double_low_conf, max_out), axis=1)]
        in_bound = in_all_bound[in_all_bound['bond_nm'].apply(lambda x : x not in balance_ids)] # 轮入债不在持仓
        return in_bound, out_bound 
    return None, None

# 在持仓中， 显示加*号
def disp_balance(s, balance_ids):
    if s in balance_ids: 
        return '*'+s
    else:
        return s

# 仅用于展示 和 保存
def display(bound, balance, in_bound, out_bound, user_zh_columns, output=None, send_email=False):
    # 持仓的股票 加 *
    balance_ids = list(balance['stock_name'])
    bound['bond_nm'] = bound['bond_nm'].apply(lambda s: disp_balance(s, balance_ids))

    # 换成中文header
    columns = bound.columns
    header_bef = [jisilu_dict[x] for x in columns] # 中文header
    dis_bound = bound.rename(columns = jisilu_dict) 

    # 指定优先显示的列&列的顺序
    header = user_zh_columns + [col for col in header_bef if col not in user_zh_columns]  # 添加header的顺序
    # 显示百分号
    for col in [u'涨跌幅', u'正股涨跌', u'溢价率', u'转债占比', u'到期税前收益', u'到期税后收益', u'波动率', u'换手率']:
        dis_bound[col] = dis_bound[col].apply(lambda x: format(x/100, ".2%"))

    # to_html & save
    if output:
        topk = balance_manege(dis_bound.index.size)
        logging.debug(in_bound)
        logging.debug(out_bound)
        if in_bound.empty:
            in_ids = []
        else:
            in_bound['bond_nm'] =in_bound['bond_nm'].apply(lambda s: disp_balance(s, balance_ids))
            in_ids = list(in_bound['bond_nm'])
        if out_bound.empty:
            out_ids = []
        else:
            out_bound['bond_nm'] = out_bound['bond_nm'].apply(lambda s: disp_balance(s, balance_ids))
            out_ids = list(out_bound['bond_nm'])

        ori_html = toHTML(dis_bound, in_ids, out_ids, topk)
        with open(output, 'w', encoding='utf8') as f:
            f.write(ori_html)
            f.close()
    
    if send_email:
        sendEmail(ori_html, '可转债脉冲轮动', '可转债脉冲轮动')
    
    return dis_bound.loc[:, header]


def main(argv):
    logging.info("args: %s" %" ".join(argv)) 
    # policy = ['period', 'pulse']
    policy = argv[1] 
    bound = read_data()  #读市场
    balance = read_balancing()  #读持仓
    if policy == 'period':
        in_bound = periodWheel(bound, double_low_conf)
        result = display(bound, balance, in_bound, None, user_zh_columns=double_low_conf['user_zh_columns'])
        logging.debug(result)
    elif policy == 'pulse':
        pulse_path = '/root/workSpace/investProject/ConvertBondWheel/data/pulse_alarm.html'
        in_bound, out_bound = pulseWheel(bound, balance, double_low_conf)
        if out_bound is not None:
            result = display(bound, balance, in_bound, out_bound, user_zh_columns=double_low_conf['user_zh_columns'], output=pulse_path, send_email=True)
            logging.debug(result)
    else:
        logging.error("Parameter policy error!!")


if __name__ == "__main__":
    main(sys.argv)

