# ConvertBondWheel
jojo and me

# 环境(python)
install conda

pip install  tushare

conda install scrapy,pandas,matplotlib

## 概述 
该项目主要用于一些简单量化策略，当前主要是 可转债。

|-- ConvertBondWheel
|   `-- spiders
|-- data
`-- policy
    |-- analysis
    |-- angelkillerwang
    |-- backTest
    `-- double_low


1. 可转债轮动双低策略，包括爬虫和轮动策略两部分， 爬虫源码： ./ConvertBondWhell/spider, 爬虫数据： ./data  策略： ./policy/double_low(策略详情： https://www.notion.so/7f2de7ac14ea4792ba69fe7b39181ecf),

2. backTest 基于tushare的一些股票回测方案(todo)

3. angelkill的圆弧策略(需配合回测)

4. 港股打新策略分析(todo)

注：可在每个策略目录下查看README，了解详情