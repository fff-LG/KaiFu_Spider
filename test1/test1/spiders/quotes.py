import scrapy
from ..items import Test1Item


class QuotesSpider(scrapy.Spider):
    name = "quotes"     #项目唯一名字，用来区分不同的spider
    allowed_domains = ["quotes.toscrape.com"]       #允许爬取的域名，如果初始或者后续的请求链接不是这个域名下的，则请求链接会被过滤掉
    start_urls = ["https://quotes.toscrape.com"]    #包含了Spider在启动时爬取的URL列表，初始请求是由它来定义的

    def parse(self, response, **kwargs):          #Spider 的一个方法。在默认情况下，start_urls 里面的链接构成的请求完成下载后，parse 方法就会被调用，返回的响应就会作
                                                  #为唯一的参数传递给 parse 方法。该方法负责解析返回的响应、提取数据或者进一步生成要处理的请求。
        response = response.replace(encoding='utf-8')
        quotes = response.css('div.quote')
        for quote in quotes:
            item = Test1Item()
            item["text"] = quote.css('span.text::text').extract_first("")
            item["author"] = quote.css('small.author::text').extract_first("")
            item["tags"] = quote.css('div.tags a.tag::text').extract()
            yield item
        href = response.css("li.next a::attr(href)").extract_first("")
        next_url = response.urljoin(href)
        yield scrapy.Request(next_url, callback=self.parse)