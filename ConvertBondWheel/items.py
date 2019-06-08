# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ConvertbondwheelItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    bond_id = scrapy.Field()
    bond_nm = scrapy.Field()
    price = scrapy.Field()
    increase_rt = scrapy.Field()
    stock_nm = scrapy.Field()
    sprice = scrapy.Field()
    sincrease_rt = scrapy.Field()
    pb = scrapy.Field()
    convert_price = scrapy.Field()
    convert_value = scrapy.Field()
    premium_rt = scrapy.Field()
    # _bond_value = scrapy.Field()
    rating_cd = scrapy.Field()
    put_convert_price = scrapy.Field()
    force_redeem_price = scrapy.Field()
    convert_amt_ratio = scrapy.Field()
    short_maturity_dt = scrapy.Field()
    year_left = scrapy.Field()
    ytm_rt = scrapy.Field()
    ytm_rt_tax = scrapy.Field()
    volume = scrapy.Field()
    value_score = scrapy.Field()

    pass
