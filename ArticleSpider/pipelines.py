# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json

import MySQLdb
import MySQLdb.cursors

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi


class ArticleImagePipeline(ImagesPipeline):
    """
    存储图片文件
    """

    def item_completed(self, results, item, info):
        # results like this: <class 'list'>: [(True, {'url': 'http://jbcdn2.b0.upaiyun.com/2016/04/4a043f41f5b2e7764b45919c95078c9f.jpg', 'path': 'full/4e2da4795d7525d292c45ac4cc7df0bcacf45e47.jpg', 'checksum': '3bd0183f26c93bf5e8fb2af2938e9562'})]
        if "img_url" in item:
            for ok, value in results:
                img_path = value['path']
            item['img_file_path'] = img_path
        return item


class JsonWithEncodingPipeline(object):
    """
    存储json文件
    """

    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


class JsonExporterPipeline(object):
    """
    使用scrapy的JsonItemExporter来导出json文件
    """

    def __init__(self):
        self.file = open('article_export.json', 'wb', encoding='utf-8')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()


class MysqlPipeline(object):
    """
    同步的mysql的操作
    """
    def __init__(self):
        self.conn = MySQLdb.connect('localhost', 'root', '1234', 'article_spider', charset='utf8', use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        sql_str = """
            insert into jobbole_article (url, url_obj_id, title, pub_date, cate, 
            fav_num, vote_num, comment_num, content, img_url, img_file_path) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        data = dict(item)
        self.cursor.execute(sql_str, (
            data['url'], data['url_obj_id'], data['title'], data['pub_date'],
            data['cate'], data['fav_num'], data['vote_num'],
            data['comment_num'], data['content'], data['img_url'],
            data['img_file_path']))
        self.conn.commit()
        return item

    def spider_closed(self, spider):
        self.cursor.close()


class MysqlTwistedPipeline(object):
    """
    使用Twisted将mysql的操作变成异步
    """

    def __init__(self, db_pool):
        self.db_pool = db_pool

    # @classmethod
    # def from_settings(cls, settings):
    #     db_params = dict(
    #         host=settings.get('MYSQL_HOST'),
    #         db=settings.get('MYSQL_DB'),
    #         user=settings.get('MYSQL_USER'),
    #         passwd=settings.get('MYSQL_PASSWORD'),
    #         charset='utf8',
    #         cursorclass=MySQLdb.cursors.DictCursor,
    #         use_unicode=True
    #     )
    #     db_pool = adbapi.ConnectionPool('MySQLdb', **db_params)
    #     return cls(
    #         db_pool=db_pool
    #     )

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        db_params = dict(
            host=settings.get('MYSQL_HOST'),
            db=settings.get('MYSQL_DB'),
            user=settings.get('MYSQL_USER'),
            passwd=settings.get('MYSQL_PASSWORD'),
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        db_pool = adbapi.ConnectionPool('MySQLdb', **db_params)
        return cls(
            db_pool=db_pool
        )

    def process_item(self, item, spider):
        query = self.db_pool.runInteraction(self._insert, item)
        # 处理异常
        query.addErrback(self._handle_error, item, spider)
        return item

    def _handle_error(self, failure, item, spider):
        # 处理异步操作的异常
        print(failure)

    def _insert(self, cursor, item):
        sql_str = """
                    insert into jobbole_article
                    (url, url_obj_id, title, pub_date, cate, fav_num,
                     vote_num, comment_num, content, img_url, img_file_path) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
        cursor.execute(sql_str, (
            item['url'], item['url_obj_id'], item['title'], item['pub_date'],
            item['cate'], item['fav_num'], item['vote_num'],
            item['comment_num'], item['content'], item['img_url'],
            item['img_file_path']))


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item
