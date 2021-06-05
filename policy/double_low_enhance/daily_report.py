#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from os import path
from numpy.lib.function_base import disp
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
print(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.utils import parseaddr, formataddr
import smtplib
import time
import pandas as pd
import matplotlib.pyplot as plt
import pandas as pd
from alarm import read_data, read_balancing

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

def timeStr():
    t = time.strftime(str("%Y-%m-%d %H:%M:%S"), time.localtime())
    s = '[%s]' % t
    return s

def toHTML(data, columns, indexs):
    # 数据只显示当天
    dis_data = pd.DataFrame(data.iloc[-1, 1:].values.reshape(3, -1), columns=columns, index=indexs)
    # 显示百分号
    col = u'溢价率'
    dis_data[col] = dis_data[col].apply(lambda x: format(x/100, ".2%"))
    ori_html = dis_data.to_html()

    #set table style
    ori_html = ori_html.replace("<table", '<table style="border-collapse: collapse;"')

    return ori_html

def sendEmail(content, add, title, items, png_path):

    # send email
    from_addr = 'luoyu091@163.com'
    password = 'ZIVRTJYTZTGODWUX'
    to_addr = ['381336925@qq.com', 'moonwalkings@vip.qq.com']
    smtp_server = 'smtp.163.com'
    stime = timeStr()  

    msg = MIMEMultipart('mixed')
    msg['From'] = _format_addr('%s <%s>' % (add, from_addr))
    msg['To'] = ",".join(to_addr) 
    msg['Subject'] = Header('%s %s' % (title, stime), 'utf-8').encode()

    # 表格
    context = MIMEText(content,_subtype='html', _charset='utf-8')
    msg.attach(context)

    # 图
    content = '<p> 当日图表</p>'
    for item in  items:
        content += '<p> <img src="cid:%s" height="200" width="600"></p>' %item
        # 读图
        with open("%s/%s.png" %(png_path, item), "rb") as f:
            img = MIMEImage(f.read())
            img.add_header('Content-ID', item) 
            msg.attach(img)

    context = MIMEText(content,_subtype='html', _charset='utf-8')
    msg.attach(context)
   
   # 发送部分
    server = smtplib.SMTP_SSL(smtp_server, 465)
    # server.set_debuglevel(1)
    server.ehlo(smtp_server)
    server.login(from_addr, password)
    server.sendmail(from_addr, to_addr, msg.as_string())
    server.quit()

def plot_(df, item, item_ch, save):
    fig = plt.figure(figsize=(9, 3))
    x=list(df.index)

    plt.plot(x, df['b_mean_%s' %item], 'o-', label='组合均值')
    plt.plot(x, df['a_mean_%s' %item], 'o-', label='双低均值')
    plt.plot(x, df['a_median_%s'%item], 'o-', label='双低中位数')

    plt.legend()
    plt.xticks(x, list(df.date))
    plt.title(item_ch)
    if save:
        plt.savefig(save)

def append_abstract(bound, balance, items):
    abstract = []
    for item in items:
        abstract.append(balance[item].mean())
    for item in items:
        abstract.append(bound[item].mean())
    for item in items:
        abstract.append(bound[item].median())
    return abstract 


def main():
    item_dict= {'price':'价格', 'dblow':'双低值', 'premium_rt':'溢价率'}
    report_file="/root/workSpace/investProject/ConvertBondWheel/data/daily_report.csv"

    # 读当天可转债数据， 把报表需要的值写到文件里
    bound = read_data()  #读市场
    balance_ids = read_balancing()  #读持仓
    balance = bound[bound['bond_nm'].apply(lambda s: s in list(balance_ids['stock_name']))]

    # 读取当次数据
    his_df = pd.read_csv(report_file, dtype={'date':str})
    abstract = append_abstract(bound, balance, list(item_dict.keys()))
    s = '%s' % time.strftime(str("%Y%m%d"), time.localtime())
    today_df = pd.DataFrame(abstract.insert(0, s), columns=his_df.columns)
    # 检查最近一次写入时间， 避免多次重复写入
    report_df = pd.concat([his_df, today_df]).drop_duplicates(subset=['date'], keep='last')
    report_df = report_df.sort_values('date', ascending=True)
    # 保存最新数据
    report_df.to_csv(report_file, index=False, encoding='utf8',float_format='%.2f')

    # 报表
    ori_html = toHTML(report_df, columns=list(item_dict.values()), indexs=['组合均值', '双低均值', '双低中值'])

    # 画图
    png_path = '/root/workSpace/investProject/ConvertBondWheel/data'
    for item, item_ch in item_dict.items():
        plot_(report_df, item, item_ch, "%s/%s.png" %(png_path, item))

    #发邮件
    sendEmail(ori_html, "可转债日报", '可转债日报', list(item_dict.keys()), png_path)

if __name__ == "__main__":
    main()

