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
import json
import pandas as pd
import matplotlib.pyplot as plt
import pandas as pd
from alarm import read_data, read_balancing
from policy.common.utils import  sendEmail, dayStr

def toHTML(data, columns, indexs):
    # 数据只显示当天
    # 调整列顺序
    cols = ['balance_average_price', 'market_average_price', 'market_median_price', 'balance_average_dblow', 'market_average_dblow', 'market_median_dblow', 'balance_average_premium_rt', 'market_average_premium_rt', 'market_median_premium_rt']
    display_df = pd.DataFrame(data.iloc[-1, :][cols].values.reshape(-1, 3).T, columns=columns, index=indexs).loc[:, [u'价格', u'溢价率', u'双低值']]
    # 显示百分号
    col = u'溢价率'
    display_df[col] = display_df[col].apply(lambda x: format(x, ".2%"))
    ori_html = display_df.to_html()

    #set table style
    ori_html = ori_html.replace("<table", '<table style="border-collapse: collapse;"')

    return ori_html

def to_email(contents, items, png_path):

    msg = MIMEMultipart('mixed')

    # 表格
    for content in contents:
        context = MIMEText(content,_subtype='html', _charset='utf-8')
        msg.attach(context)

    # 图
    content = '<p> </p>'
    for item in  items:
        content += '<p> <img src="cid:%s" height="300" width="800"></p>' %item
        # 读图
        with open("%s/%s.png" %(png_path, item), "rb") as f:
            img = MIMEImage(f.read())
            img.add_header('Content-ID', item) 
            msg.attach(img)
    context = MIMEText(content,_subtype='html', _charset='utf-8')
    msg.attach(context)

    #发送
    sendEmail(msg, "可转债日报", "可转债日报")

def plot_(df, values, keys, png_path):
    x=list(range(df.index.size))

    for item, item_ch in values.items():
        fig = plt.figure(figsize=(12, 5))
        for key, keys_ch in keys.items():
            plt.plot(x, df['%s_%s' %(key, item)], 'o-', label=keys_ch)

        plt.legend(loc="upper left", bbox_to_anchor=(0, 0.85))
        plt.xticks(x, [t.strftime("%Y%m%d") for t in list(df.date)], rotation=35)
        plt.title(item_ch)
        if png_path:
            plt.savefig("%s/%s.png" %(png_path, item))

def get_reports_from_bond(bond, balance, values, keys):
    reports = {} 
    for v in values:
        for key in keys:
            if key.split('_')[0] == 'market':
                df = bond 
            else:
                df = balance
            if key.split('_')[1] == 'average':
                reports["%s_%s" %(key, v)] = df[v].mean()
            else:
                reports["%s_%s" %(key, v)] = df[v].median()

    return reports 


def get_market_distribute(bond, balance, market_distribute_index, market_distribute_columns):
    bonds_size = bond.index.size
    percents =[float(x.strip('%').replace("市场前", ""))/100 for x in market_distribute_index]

    dblow = []
    market_count= []
    banlance_count = []
    for per in percents:
        bondary = int(per * bonds_size)
        bond = bond.sort_values('dblow', ascending=True)
        tmp_bond = bond[:bondary]#.sort_values('dblow', ascending=True)
        tmp_bond.reset_index(inplace=True, drop=True)
        tmp_dblow = tmp_bond.iloc[-1]['dblow']
        dblow.append(tmp_dblow)
        market_count.append(tmp_bond.index.size)
        banlance_count.append(balance[balance['dblow'] < tmp_dblow].index.size)
    df = pd.DataFrame([dblow, market_count, banlance_count], columns =market_distribute_index, index=market_distribute_columns).T
    df[[u'市场转债个数', u'组合转债个数']] = df[[u'市场转债个数', u'组合转债个数']].astype(int)
    ori_html = df.to_html()
    ori_html = ori_html.replace("<table", '<table style="border-collapse: collapse;"')

    return ori_html 
    

def main():
    values_dict= {'price':'价格', 'dblow':'双低值', 'premium_rt':'溢价率'}
    keys_dict= {'balance_average':'组合均值', 'market_average':'市场均值', 'market_median':'市场中值'}
    market_distribute_index = ['市场前5%','市场前10%','市场前15%','市场前20%','市场前50%']
    market_distribute_columns = [u'双低值', u'市场转债个数', u'组合转债个数']
    report_file="/root/workSpace/investProject/ConvertBondWheel/data/daily_report.json"

    # 读当天可转债数据， 把报表需要的值写到文件里
    bond = read_data()  #读市场
    balance_names = read_balancing()  #读持仓
    balance = bond[bond['bond_nm'].apply(lambda s: s in balance_names)]

    # 读取当次数据
    today_reports = get_reports_from_bond(bond, balance, list(values_dict.keys()), list(keys_dict.keys()))
    today_reports['date'] = dayStr()
    today_df = pd.read_json(json.dumps([today_reports]))

    # 读历史数据
    history_df = pd.read_json(report_file)
    report_df = pd.concat([history_df, today_df]).drop_duplicates(subset=['date'], keep='last')
    report_df = report_df.sort_values('date', ascending=True)

    # 保存最新数据
    report_df.to_json(report_file, orient="records")
    print(report_df)

    # 报表 1
    report1 = toHTML(report_df, columns=list(values_dict.values()), indexs=list(keys_dict.values()))
    # 报表2 市场分布
    market_distrubute = get_market_distribute(bond, balance, market_distribute_index, market_distribute_columns)
    print(market_distrubute)

    # 画图
    png_path = '/root/workSpace/investProject/ConvertBondWheel/data'
    # for item, item_ch in values_dict.items():
    plot_(report_df, values_dict, keys_dict, png_path)

    #发邮件
    to_email([report1, market_distrubute], list(values_dict.keys()), png_path)

if __name__ == "__main__":
    main()

