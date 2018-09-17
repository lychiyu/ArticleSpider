# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import re
from datetime import datetime, timedelta

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


def get_before_datetime(days=0):
    return datetime.now() - timedelta(days=days)


def process_job_pub_time(value):
    date_str = value.split(' ')[0].strip()
    re_result = re.compile('(\d+)天前').search(date_str)
    if re_result:
        return get_before_datetime(int(re_result.group(1)))
    if date_str in ('今天', '今日') or re.compile('\d+:\d+').match(date_str):
        return get_before_datetime()
    if date_str in ('昨天', '昨日'):
        return get_before_datetime(1)
    if date_str in ('前天', '前日'):
        return get_before_datetime(2)
    return datetime.strptime(date_str, '%Y-%m-%d')


def remove_splash(value):
    # 去除文本中的斜杆/
    return value.replace('/', '').strip()


def remove_enter(value):
    # 去除回车换行符
    return value.replace('\n', '').strip()


def handle_jobaddr(value):
    addr_list = value.split('\n')
    addr_list = [item.strip() for item in addr_list if item.strip() != '查看地图']
    return ''.join(addr_list).replace('-', '').replace(' ', '').strip()


def get_min_degree_need(value):
    if value == "学历不限":
        return "不限"
    return value[:2]


def get_min_salary(value):
    result = re.compile(r'(\d+)k.*?').match(value)
    return 0 if not result else int(result.group(1))


def get_max_salary(value):
    result = re.compile(r'.*?-(\d+)k.*?').match(value)
    if result:
        return int(result.group(1))
    result = re.compile(r'(\d+)k.*?以上').match(value)
    if result:
        return int(result.group(1))
    return 100000


def get_min_year(value):
    year_str = value.replace('经验', '')
    if year_str == "应届毕业生":
        return -1
    result = re.compile(r'(\d+)-.*?|(\d+)年.*?').match(year_str)
    if result:
        return int(result.group(1) if result.group(1) else result.group(2))
    return 0


def get_max_year(value):
    year_str = value.replace('经验', '')
    if year_str == "应届毕业生":
        return -1
    result = re.compile(r'.*?-(\d+)年').match(year_str)
    if result:
        return int(result.group(1))
    result = re.compile(r'(\d+)年.*?以上.*?').match(year_str)
    if result:
        return 100
    return 0


class LagouJobItem(scrapy.Item):
    # 拉勾网职位信息item
    title = scrapy.Field()
    url = scrapy.Field()
    url_obj_id = scrapy.Field()
    salary_min = scrapy.Field(
        input_processor=MapCompose(get_min_salary),
    )
    salary_max = scrapy.Field(
        input_processor=MapCompose(get_max_salary),
    )
    job_city = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    year_min = scrapy.Field(
        input_processor=MapCompose(remove_splash, get_min_year),
    )
    year_max = scrapy.Field(
        input_processor=MapCompose(remove_splash, get_max_year),
    )
    degree_need = scrapy.Field(
        input_processor=MapCompose(remove_splash, get_min_degree_need),
    )
    job_type = scrapy.Field()
    tags = scrapy.Field(
        input_processor=Join(','),
    )
    pub_time = scrapy.Field(
        input_processor=MapCompose(process_job_pub_time),
    )
    advantage = scrapy.Field()
    desc = scrapy.Field(
        input_processor=MapCompose(remove_tags, remove_enter),
    )
    job_address = scrapy.Field(
        input_processor=MapCompose(remove_tags, handle_jobaddr),
    )
    company_name = scrapy.Field()
    company_dev = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    company_scope = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    company_domain = scrapy.Field(
        input_processor=MapCompose(remove_splash),
    )
    company_url = scrapy.Field()
    crawl_time = scrapy.Field()
    crawl_update = scrapy.Field()
