# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
from datetime import datetime

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join
from w3lib.html import remove_tags


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


class LagouJobItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


def remove_splash(value):
    # 去除文本中的斜杆/
    return value.replace('/', '').strip()


def handle_jobaddr(value):
    addr_list = value.split('\n')
    addr_list = [item.strip() for item in addr_list if item.strip() != '查看地图']
    return ''.join(addr_list)


class LagouJobItem(scrapy.Item):
    # 拉勾网职位信息item
    title = scrapy.Field()
    url = scrapy.Field()
    url_obj_id = scrapy.Field()
    salary_min = scrapy.Field()
    salary_max = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    year_min = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    year_max = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    degree_need = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    job_type = scrapy.Field()
    tags = scrapy.Field(
        input_processor=Join(','),
    )
    pub_time = scrapy.Field()
    advantage = scrapy.Field()
    desc = scrapy.Field(
        input_processor=MapCompose(remove_tags),
    )
    job_address = scrapy.Field(
        input_processor=MapCompose(remove_tags, handle_jobaddr),
    )
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    crawl_time = scrapy.Field()
    crawl_update = scrapy.Field()
