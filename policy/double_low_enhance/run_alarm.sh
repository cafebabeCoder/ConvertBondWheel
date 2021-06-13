#!/bin/bash
export PATH=$PATH:/root/anaconda3/bin:/root/anaconda3/envs/scrapy_ts/bin

cur_date=$(date '+%Y-%m-%d %H:%M:%S')
echo "---------$cur_date------"

# 爬虫爬集思录
# echo "---------scrapy---------"
# cd /root/workSpace/investProject/ConvertBondWheel/ConvertBondWheel/spiders
# scrapy crawl jisilu  
# scrapy crawl xueqiu 
sh /root/workSpace/investProject/ConvertBondWheel/policy/double_low_enhance/run_spider.sh

# 运行监控程序
echo "--------alarm-----------"
/root/anaconda3/envs/scrapy_ts/bin/python /root/workSpace/investProject/ConvertBondWheel/policy/double_low_enhance/alarm.py pulse

# 替换当前文件为历史文件
echo "-----replace file-------"
cp /root/workSpace/investProject/ConvertBondWheel/data/jisiluConvertBound.csv /root/workSpace/investProject/ConvertBondWheel/data/jisiluConvertBound_pre.csv

echo -e " "
