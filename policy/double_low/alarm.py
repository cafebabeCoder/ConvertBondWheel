#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
import time
import datetime
import pandas as pd
import os.path

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

def timeStr():
    t = time.strftime(str("%Y-%m-%d %H:%M:%S"), time.localtime())
    s = '[%s]' % t
    return s

def toHTML(data, ins, outs, top_k):
    ori_html = data.to_html()

    #set table style
    ori_html = ori_html.replace("<table", '<table style="border-collapse: collapse;"')

    # set color
    red = ' style="color:red;"'  # in
    green = ' style="color:green;"' # out

    for id in ins:
        st = "<td>%s</td>" % id
        replace_st = "<td%s>%s</td>" %(red, id)
        ori_html = ori_html.replace(st, replace_st)
    for id in outs:
        st = "<td>%s</td>" % id
        replace_st = "<td%s>%s</td>" %(green, id)
        ori_html = ori_html.replace(st, replace_st)

    for id in data.iloc[:top_k, 1]:
        replace_st = "<b>%s<b>" %id
        ori_html = ori_html.replace(str(id), replace_st)

    # set topk
    st = '<th>%d</th>' %top_k
    replace_st = '<td></td></tr><tr><th>%d</th>' %top_k
    ori_html = ori_html.replace(st, replace_st)

    with open('datatable.html','w') as f:
        f.write(ori_html)
        f.close()

    return ori_html

def sendEmail(content):

    # send email
    from_addr = 'luoyu091@163.com'
    password = 'ZIVRTJYTZTGODWUX'
    to_addr = ['381336925@qq.com', 'moonwalkings@vip.qq.com']
    smtp_server = 'smtp.163.com'
    stime = timeStr()  

    msg = MIMEText(content, 'html', 'utf-8')
    msg['From'] = _format_addr('可转债机器人 <%s>' % from_addr)
    # msg['To'] = _format_addr('test <%s>' % ",".join(to_addr))
    msg['To'] = ",".join(to_addr) 
    msg['Subject'] = Header('可转债双低轮动排名 %s' % stime, 'utf-8').encode()

    server = smtplib.SMTP_SSL(smtp_server, 465)
    # server.set_debuglevel(1)
    server.ehlo(smtp_server)
    server.login(from_addr, password)
    server.sendmail(from_addr, to_addr, msg.as_string())
    server.quit()

# 如果是最后一次拉数据， 也要发邮件
def isLastTrade():
    time_now = datetime.datetime.now()
    hour = time_now.hour
    mins = time_now.minute
    if hour == 15 and mins < 10:
        return True
    else:
        return False

def join_int_list(ilist, sep=","):
    return sep.join([str(i) for i in ilist])

def main():
    bound_file = '/root/workSpace/investProject/ConvertBondWheel/data/jisiluConvertBound.csv'
    # 判断爬虫是否正常， 不正常发邮件提醒
    if not os.path.isfile(bound_file):
        content = "%s is not exist!" % bound_file
        sendEmail(content)
        print("file not exist!")
        return

    # 读取当次数据
    data = pd.read_csv(bound_file, skiprows=-1).iloc[:,:-1]

    # 读取上次数据
    previous = pd.read_csv("/root/workSpace/investProject/ConvertBondWheel/data/jisiluConvertBound_pre.csv")

    # 对比， 如果top 15%发生变化， 发邮件
    top_k = 15 # int(len(data.iloc[:, 1]) * 0.15)
    top_bound =  set(data.iloc[:top_k, 1])
    top_previous_bound = set(previous.iloc[:top_k, 1])
    outs = list(top_bound - top_previous_bound)
    ins = list(top_previous_bound - top_bound)

    print("topk=%d\ntop_bound=%s\ntop_previous_bound=%s\nouts=%s\nins=%s\nouts_size=%d\nins_size=%d" \
        %(top_k, join_int_list(top_bound), join_int_list(top_previous_bound), join_int_list(outs), join_int_list(ins), len(outs), len(ins)))

    if len(outs)>0 or len(ins)>0 or isLastTrade():
        print("send")
        html = toHTML(data, ins, outs, top_k)
        sendEmail(html)

if __name__ == "__main__":
    main()

