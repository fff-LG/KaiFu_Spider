# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class KaifuspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()       #博客标题
    url = scrapy.Field()         #博客url
    time = scrapy.Field()        #发表时间
    articleTags = scrapy.Field() #博客标签
    content = scrapy.Field()     #文章内容
    like_count = scrapy.Field()  #喜欢数
    goldPan = scrapy.Field()     #赠金笔数
    read = scrapy.Field()        #阅读数
    comments = scrapy.Field()    #评论数
    reproduce = scrapy.Field()   #转载量
    collections = scrapy.Field() #收藏量

