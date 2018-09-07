# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
from datetime import datetime

import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def processor_pub_date(value):
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except Exception:
        return datetime.now().date()


class JobboleArticleItem(scrapy.Item):
    url = scrapy.Field(
        # 可以为item字段添加处理函数
        # input_processor=MapCompose(processor_url),
        # output_processor=TakeFirst() # 只取第一个
    )
    url_obj_id = scrapy.Field()
    title = scrapy.Field()
    pub_date = scrapy.Field(
        input_processor=processor_pub_date
    )
    cate = scrapy.Field()
    tag = scrapy.Field()
    fav_num = scrapy.Field()
    vote_num = scrapy.Field()
    comment_num = scrapy.Field()
    content = scrapy.Field()
    img_url = scrapy.Field()
    img_file_path = scrapy.Field()
