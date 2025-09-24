# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class MongoDBPipeline(object):

    def __init__(self,connection_string,database):
        self.connection_string = connection_string
        self.database = database
        self.collection_name = 'blog_item'


    def process_item(self, item, spider):

        adapter = ItemAdapter(item)  #ItemAdapter 是 Scrapy 提供的工具类，用于统一操作 Item 对象（爬取到的数据结构）

        # 检查item中是否包含url字段
        if not adapter.get('url'):
            spider.logger.warning("Item 缺少 'url' 字段，无法进行去重检查")
            return item

        # 查询数据库中是否已存在相同url，去重
        existing_item = self.db[self.collection_name].find_one(
            {'url': adapter['url']}
        )

        if existing_item:
            spider.logger.info(f"URL 已存在，跳过存储: {adapter['url']}")
        else:
            # 不存在则插入数据
            self.db[self.collection_name].insert_one(dict(item))
            spider.logger.info(f"成功存储新数据: {adapter['url']}")

        return item


    @classmethod
    def from_crawler(cls,crawler):
        return cls(
            connection_string=crawler.settings.get('MONGODB_CONNECTION_STRING'),
            database=crawler.settings.get('MONGODB_DATABASE')
        )

    def open_spider(self,spider):
        self.client = pymongo.MongoClient(self.connection_string)
        self.db = self.client[self.database]

    def close_spider(self,spider):
        self.client.close()