# -*- coding: utf-8 -*-
from datetime import datetime

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from ArticleSpider.items import LagouJobItemLoader, LagouJobItem
from ArticleSpider.utils.common import get_md5


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']

    rules = (
        Rule(LinkExtractor(allow=(r'zhaopin/.*',)), follow=True),
        Rule(LinkExtractor(allow=(r'gongsi/j\d+.html',)), follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_job', follow=True),
    )

    headers = {
        "Connection": "keep-alive",
        "Host": "www.lagou.com",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36"
    }

    def parse_job(self, response):
        item_loader = LagouJobItemLoader(item=LagouJobItem(), response=response)
        item_loader.add_css('title', '.job-name::attr(title)')
        item_loader.add_value('url', response.url)
        item_loader.add_value('url_obj_id', get_md5(response.url))
        item_loader.add_css('salary_min', '.job_request .salary::text')
        item_loader.add_css('salary_max', '.job_request .salary::text')
        item_loader.add_xpath('job_city', '//dd[@class="job_request"]/p/span[2]/text()')
        item_loader.add_xpath('year_min', '//dd[@class="job_request"]/p/span[3]/text()')
        item_loader.add_xpath('year_max', '//dd[@class="job_request"]/p/span[3]/text()')
        item_loader.add_xpath('degree_need', '//dd[@class="job_request"]/p/span[4]/text()')
        item_loader.add_xpath('job_type', '//dd[@class="job_request"]/p/span[5]/text()')
        item_loader.add_css('tags', '.position-label li::text')
        item_loader.add_css('pub_time', '.publish_time::text')
        item_loader.add_css('advantage', '.job-advantage p::text')
        item_loader.add_css('desc', '.job_bt div')
        item_loader.add_css('job_address', '.work_addr')
        item_loader.add_css('company_name', '.job_company dt a img::attr(alt)')
        item_loader.add_css('company_url', '.job_company dt a::attr(href)')
        item_loader.add_value('crawl_time', datetime.now())
        job_item = item_loader.load_item()
        return job_item

    def start_requests(self):
        """
        重写start_requests方法，来给请求加上cookies
        :return:
        """
        cookies = {
            "HMACCOUNT": "633C0B24C6D84954",
            "Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6": "1536476808",
            "Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6": "1536476681",
            "JSESSIONID": "ABAAABAAAFCAAEGEFB09B114CDF9889A34493E8790D18F5",
            "LGRID": "20180909150648-eb08c4fc-b3fe-11e8-8ce4-525400f775ce",
            "LGSID": "20180909150627-de8c5600-b3fe-11e8-8ce4-525400f775ce",
            "LGUID": "20180909150627-de8c582d-b3fe-11e8-8ce4-525400f775ce",
            "LG_LOGIN_USER_ID": "27189cea03cce3c4edce8b783df1c093bdd37a4f0140ff29",
            "PRE_HOST": '',
            "PRE_LAND": "https%3A%2F%2Fpassport.lagou.com%2Flogin%2Flogin.html",
            "PRE_SITE": '',
            "PRE_UTM": '',
            "TG-TRACK-CODE": "index_user",
            "X_HTTP_TOKEN": "e096a615e745e028c21eb8c0c10cb7b0",
            "_ga": "GA1.2.881516276.1536476787",
            "_gid": "GA1.2.929232426.1536476787",
            "_putrc": "88B2471F760D06A7",
            "gate_login_token": "2afd5c6c903770c0467e34edbc21eac117505a51f314bba2",
            "hasDeliver": "171",
            "index_location_city": "%E5%85%A8%E5%9B%BD",
            "login": "true",
            "unick": "%E5%88%98%E5%BD%B1",
            "user_trace_token": "20180909150622-6b77cfc9-4389-483c-a8b1-4dc9440f410e"
        }
        yield scrapy.Request(url=self.start_urls[0], cookies=cookies, headers=self.headers, callback=self.parse,
                             dont_filter=True)

    def _build_request(self, rule, link):
        """
        重写_build_request方法，来给请求加上headers
        :param rule:
        :param link:
        :return:
        """
        r = scrapy.Request(url=link.url, headers=self.headers, callback=self._response_downloaded)
        r.meta.update(rule=rule, link_text=link.text)
        return r
