#!/bin/bash
export PATH=$PATH:/root/anaconda3/bin:/root/anaconda3/envs/scrapy_ts/bin

cur_date=$(date '+%Y-%m-%d %H:%M:%S')
echo "---------$cur_date------"

# 运行 报表程序
echo "--------alarm-----------"
/root/anaconda3/envs/scrapy_ts/bin/python /root/workSpace/investProject/ConvertBondWheel/policy/double_low_enhance/daily_report.py

echo -e " "
