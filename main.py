# coding: utf-8

"""
 Created by liuying on 2018/9/6.
"""
import sys, os
from scrapy.cmdline import execute

# 将当前path添加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(['scrapy', 'crawl', 'jobbole'])