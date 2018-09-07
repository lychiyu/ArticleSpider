# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy.http import Request
from scrapy.loader import ItemLoader
from urllib import parse

from ArticleSpider.items import JobboleArticleItem
from ArticleSpider.utils.common import get_md5


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        # 获取文章列表页的所有文章节点
        post_nodes = response.css('#archive .post-thumb a')
        for post_node in post_nodes:
            post_url = post_node.css("::attr(href)").extract_first('')
            img_url = post_node.css('img::attr(src)').extract_first('')
            # 去解析文章详情页
            yield Request(url=parse.urljoin(response.url, post_url),
                          meta={'img_url': parse.urljoin(response.url, img_url)},
                          callback=self.parse_article)

        # 获取下一页链接，并去解析文章列表页
        next_page = response.css('.next.page-numbers::attr(href)').extract_first('')
        if next_page:
            yield Request(url=parse.urljoin(response.url, next_page), callback=self.parse)

    def parse_article(self, response):
        article_item = JobboleArticleItem()
        # 解析文章内容
        title = response.xpath('//div[@class="entry-header"]/h1/text()').extract_first()
        pub_date = response.xpath('//div[@class="entry-meta"]/p/text()').extract_first().replace('·', '').strip()
        cate = response.xpath('//div[@class="entry-meta"]/p/a[1]/text()').extract_first()
        vote_num = response.xpath('//span[contains(@class, "vote-post-up")]/h10/text()').extract_first()
        vote_num = int(vote_num) if vote_num else 0
        fav_text = response.xpath('//span[contains(@class, "bookmark-btn")]/text()').extract_first().strip()
        fav_re_rlt = re.compile('.*?(\d+).*?').search(fav_text)
        fav_num = fav_re_rlt.group(1) if fav_re_rlt else 0
        comment_text = response.xpath('//a[@href="#article-comment"]/span/text()').extract_first().strip()
        comment_re_rlt = re.compile('.*?(\d+).*?').search(comment_text)
        comment_num = comment_re_rlt.group(1) if comment_re_rlt else 0
        content = response.xpath('//div[@class="entry"]').extract_first('')
        img_url = parse.urljoin(response.url, response.meta.get('img_url', ''))

        article_item['url'] = response.url
        article_item['url_obj_id'] = get_md5(response.url)
        article_item['title'] = title
        article_item['pub_date'] = pub_date
        article_item['cate'] = cate
        article_item['fav_num'] = fav_num
        article_item['vote_num'] = vote_num
        article_item['comment_num'] = comment_num
        article_item['content'] = content
        article_item['img_url'] = [img_url]

        """
        # 使用ItemLoader
        # 使用ItemLoader可以使得item的获取解析变成可配置，可以配置到数据库中，进行配置
        item_loader = ItemLoader(item=JobboleArticleItem(), response=response)
        item_loader.add_xpath('title', '//div[@class="entry-header"]/h1/text()')
        item_loader.add_xpath('pub_date', '//div[@class="entry-meta"]/p/text()')
        item_loader.add_xpath('cate', '//div[@class="entry-meta"]/p/a[1]/text()')
        item_loader.add_xpath('tag', '//div[@class="entry-meta"]/p/a[2]/text()')
        item_loader.add_value('url', response.url)
        item_loader.add_value('url_obj_id', get_md5(response.url))
        item_loader.add_value('img_url', [img_url])
        item_loader.add_xpath('vote_num', '//span[contains(@class, "vote-post-up")]/h10/text()')
        item_loader.add_xpath('fav_num', '//span[contains(@class, "bookmark-btn")]/text()')
        item_loader.add_xpath('comment_num', '//a[@href="#article-comment"]/span/text()')
        item_loader.add_xpath('content', '//div[@class="entry"]')
        article_item = item_loader.load_item()
        """
        yield article_item
