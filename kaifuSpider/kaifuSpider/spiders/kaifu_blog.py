import scrapy
import re # 正则表达式处理
from ..items import KaifuspiderItem

class KaifuBlogSpider(scrapy.Spider):
    name = "kaifu_blog"
    allowed_domains = ["blog.sina.com.cn"]
    start_urls = ["https://blog.sina.com.cn/kaifulee"]

    def parse(self, response, **kwargs):

        title_blocks = response.xpath('//div[@class="blog_title_h"]')

        for title_block in title_blocks:

            item = KaifuspiderItem()

            # 1.爬取博客标题title
            item['title'] = title_block.xpath('.//div[@class="blog_title"]/a/text()').extract_first("").strip()

            # 2.爬取博客url
            blog_url = title_block.xpath('.//div[@class="blog_title"]/a/@href').extract_first("").strip()
            item['url'] = response.urljoin(blog_url)  #处理相对路径，拼接为绝对路径

            # 3.爬取博客发表时间
            raw_time = title_block.xpath('.//span[@class="time SG_txtc"]/text()').extract_first("").strip()
            time_match = re.search(r'\((.*?)\)', raw_time)
            item['time'] = time_match.group(1) if time_match else raw_time

            # 4.爬取博客标签
            item["articleTags"] = title_block.xpath(
                './following-sibling::div[contains(@class, "articalTag")][1]'
                '//td[@class="blog_tag"]'
                '//h3/text() | '  # 第一页：h3直接包含文本
                './following-sibling::div[contains(@class, "articalTag")][1]'
                '//td[@class="blog_tag"]'
                '//h3//a/text() |'  # 后续页：h3下的a标签包含文本
                './following-sibling::div[contains(@class, "articalTag")][1]'
                '//td[@class="blog_class"]//a/text()' # 最后几页：在blog_class下的a标签文本
            ).extract()
            item["articleTags"] = [tag.strip() for tag in item["articleTags"] if tag.strip()]

            # 5.爬取博客文章内容
            content_parts = title_block.xpath('./following-sibling::div[contains(@class, "content") ][1]//text()').extract()
            item["content"] = "".join(part.strip() for part in content_parts if part.strip())

            # 6.爬取博客阅读数
            read_text = title_block.xpath('./following-sibling::div[contains(@class, "tagMore")][1]/a[starts-with(@id, "r_")]/following-sibling::text()[1]').extract_first("")    #“+”用于匹配相邻元素，提取数字
            read_match = re.search(r'(\d+)',read_text)
            item["read"] = int(read_match.group(1)) if read_match else 0

            # 7.爬取博客评论数
            comment_text = title_block.xpath('./following-sibling::div[contains(@class, "tagMore")][1]/a[starts-with(@id, "c_")]/following-sibling::text()[1]').extract_first("")
            comment_match = re.search(r'(\d+)',comment_text)
            item["comments"] = int(comment_match.group(1)) if comment_match else 0

            # 8.爬取博客转载量
            reproduce_text = title_block.xpath('./following-sibling::div[contains(@class, "tagMore")][1]/a[contains(@class, "zznum")]/text()').extract_first("")
            reproduce_match = re.search(r'(\d+)',reproduce_text)
            item["reproduce"] = int(reproduce_match.group(1)) if reproduce_match else 0

            # 9.爬取博客收藏量
            collect_text = title_block.xpath('./following-sibling::div[contains(@class, "tagMore")][1]/a[starts-with(@id, "f_")]/following-sibling::text()[1]').extract_first("")
            collect_match = re.search(r'(\d+)',collect_text)
            item["collections"] = int(collect_match.group(1)) if collect_match else 0

            #输出当前博客的Item数据
            yield item

            #获取下一页url并继续爬取
            #新浪博客分页按钮的href属性不是完整的URL而是JS代码，新浪博客的分页按钮是Javascript动态加载的

            # 1. 提取当前页码（从当前 URL 中解析）
            current_page_match = re.search(r'article_sort_\d+_\d+_(\d+)\.html', response.url)
            current_page = int(current_page_match.group(1)) if current_page_match else 1

            # 2. 定义总页数
            total_pages = 26

            # 3. 构造下一页 URL 并请求
            if current_page < total_pages:
                next_page = current_page + 1
                # 按照抓包的 URL 格式构造
                next_page_url = f"https://blog.sina.com.cn/s/article_sort_1197161814_10001_{next_page}.html"
                self.logger.debug(f"下一页 URL: {next_page_url}")
                yield scrapy.Request(
                    url=next_page_url,
                    callback=self.parse,
                )
            else:
                self.logger.debug("已爬取到最后一页")
