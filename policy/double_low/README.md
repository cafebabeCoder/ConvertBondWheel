# ConvertBondWheel
jojo and me

# 环境
install annaconda

conda create -n scrapy_ts scrapy

conda activate scrapy_ts

conda install scrapy,pandas,matplotlib,request

pip install  tushare

# run
clone project : /root/workSpace/investProject/ConvertBondWheel

sh /root/workSpace/investProject/ConvertBondWheel/policy/double_low/run_alarm.sh

# scrapy converboundwheel only
cd ConvertBondWheel\ConvertBondWheel\spiders

scrapy crawl jisilu

# scrapy xueqiu
(用jojo账号登陆，并获取持仓) 
cd ConvertBondWheel\ConvertBondWheel\spiders

scrapy runspider spiders\xueqiu.py (与上面jisilu可以互换)

# crontab
*/10 9-14 * * 1-5 sh /root/workSpace/investProject/ConvertBondWheel/policy/double_low/run_alarm.sh > /tmp/policy/log 2>&1 &

不能运行先检查是否有文件夹， 是否有权限
