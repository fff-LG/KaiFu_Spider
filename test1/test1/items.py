# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Test1Item(scrapy.Item):   #继承Item类，使用Field定义字段，爬取时就会使用Item
    # define the fields for your item here like:
    # name = scrapy.Field()
    text = scrapy.Field()   #每条名言的内容
    author = scrapy.Field() #作者
    tags = scrapy.Field()   #标签
