# -*- coding: utf-8 -*-

# Scrapy settings for ConvertBondWheel project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'ConvertBondWheel'

SPIDER_MODULES = ['ConvertBondWheel.spiders']
NEWSPIDER_MODULE = 'ConvertBondWheel.spiders'

# 多少天的平均成交量
VOL_DATE_AGO = 90
# 筛除掉平均成交额低于 500 万的转债
MIN_VOL = 500
# 输出目录， 格式 目录+时间.csv
OUTPUT = "/root/workSpace/investProject/ConvertBondWheel/data/"
FILENAME = 'jisiluConvertBound'
#tushare token
TOKEN = '047e2bcae2ea6c2f6f225eeb62087d27e1981988e758c82ba1997971'
# xueqiu
XUEQIU_COOKIE = "/root/workSpace/investProject/ConvertBondWheel/ConvertBondWheel/mycookie"
XUEQIU_FILENAME = "xueqiuRebalancing"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'ConvertBondWheel (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False
LOG_LEVEL = "INFO"
# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 64 

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 64 
CONCURRENT_REQUESTS_PER_IP = 64 

# Disable cookies (enabled by default)
COOKIES_ENABLED = True 

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'ConvertBondWheel.middlewares.ConvertbondwheelSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'ConvertBondWheel.middlewares.ConvertbondwheelDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'ConvertBondWheel.pipelines.ConvertbondwheelPipeline': 300,
   'ConvertBondWheel.pipelines.XueqiuPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'