import sys
import logging
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
import time
import pandas as pd
from ConvertBondWheel.items import ConvertbondwheelItem
import pandas as pd

def dayStr():
    t = time.strftime(str("%Y-%m-%d"), time.localtime())
    s = '%s' % t
    return s

def timeStr():
    t = time.strftime(str("%Y-%m-%d %H:%M:%S"), time.localtime())
    s = '[%s]' % t
    return s

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

def sendEmail(msg, sender, title):
    # send email
    from_addr = 'luoyu091@163.com'
    tok = 'ZIVRTJYTZTGODWUX'
    to_addr = ['381336925@qq.com', 'moonwalkings@vip.qq.com']
    # to_addr = ['381336925@qq.com']
    smtp_server = 'smtp.163.com'
    stime = timeStr()  

    msg['From'] = _format_addr('%s <%s>' % (sender, from_addr))
    msg['To'] = ",".join(to_addr) 
    msg['Subject'] = Header('%s %s' % (title, stime), 'utf-8').encode()

    server = smtplib.SMTP_SSL(smtp_server, 465)
    # server.set_debuglevel(1)
    server.ehlo(smtp_server)
    server.login(from_addr, tok)
    server.sendmail(from_addr, to_addr, msg.as_string())
    server.quit()


if __name__ == "__main__":
    pass
