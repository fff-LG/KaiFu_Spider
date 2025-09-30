import scrapy
import re # 正则表达式处理
from ..items import KaifuspiderItem
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
from webdriver_manager.chrome import ChromeDriverManager



class KaifuBlogSpider(scrapy.Spider):
    name = "kaifu_blog"
    allowed_domains = ["blog.sina.com.cn"]
    start_urls = ["https://blog.sina.com.cn/kaifulee"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 初始化WebDriver
        chromedriver_path = r"E:\chromedriver-win64\chromedriver.exe"  # 替换为实际路径
        self.driver = webdriver.Chrome(
            service=Service(chromedriver_path)
        )

    def closed(self, reason):
        # 爬虫关闭时退出浏览器
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()
            self.logger.info("浏览器已关闭")

    def parse(self, response, **kwargs):

        title_blocks = response.xpath('//div[@class="blog_title_h"]')

        for title_block in title_blocks:

            item = KaifuspiderItem()

            # 1.爬取博客标题title（静态
            item['title'] = title_block.xpath('.//div[@class="blog_title"]/a/text()').extract_first("").strip()

            # 2.爬取博客url（静态
            blog_url = title_block.xpath('.//div[@class="blog_title"]/a/@href').extract_first("").strip()
            item['url'] = response.urljoin(blog_url)  #处理相对路径，拼接为绝对路径

            # 3.爬取博客发表时间（静态
            raw_time = title_block.xpath('.//span[@class="time SG_txtc"]/text()').extract_first("").strip()
            time_match = re.search(r'\((.*?)\)', raw_time)
            item['time'] = time_match.group(1) if time_match else raw_time

            # 4.爬取博客标签（静态
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


            # 5.爬取博客阅读数（动态
            read_text = title_block.xpath('./following-sibling::div[contains(@class, "tagMore")][1]/a[starts-with(@id, "r_")]/following-sibling::text()[1]').extract_first("")    #“+”用于匹配相邻元素，提取数字
            read_match = re.search(r'(\d+)',read_text)
            item["read"] = int(read_match.group(1)) if read_match else 0

            # 6.爬取博客评论数（动态
            comment_text = title_block.xpath('./following-sibling::div[contains(@class, "tagMore")][1]/a[starts-with(@id, "c_")]/following-sibling::text()[1]').extract_first("")
            comment_match = re.search(r'(\d+)',comment_text)
            item["comments"] = int(comment_match.group(1)) if comment_match else 0

            # 7.爬取博客转载量（动态
            reproduce_text = title_block.xpath('./following-sibling::div[contains(@class, "tagMore")][1]/a[contains(@class, "zznum")]/text()').extract_first("")
            reproduce_match = re.search(r'(\d+)',reproduce_text)
            item["reproduce"] = int(reproduce_match.group(1)) if reproduce_match else 0

            # 8.爬取博客收藏量（动态
            collect_text = title_block.xpath('./following-sibling::div[contains(@class, "tagMore")][1]/a[starts-with(@id, "f_")]/following-sibling::text()[1]').extract_first("")
            collect_match = re.search(r'(\d+)',collect_text)
            item["collections"] = int(collect_match.group(1)) if collect_match else 0


            #发起详情页请求：通过meta传递列表页已爬取的的数据，为后续进入详情页爬取做准备
            if item['url']:
                yield scrapy.Request(
                    item['url'],
                    callback=self.parse_detail,
                    meta={'base_item': item}
                )



            #获取下一页url并继续爬取
            #新浪博客分页按钮的href属性不是完整的URL而是JS代码，新浪博客的分页按钮是Javascript动态加载的

            # 提取当前页码（从当前 URL 中解析）
        current_page_match = re.search(r'article_sort_\d+_\d+_(\d+)\.html', response.url)
        current_page = int(current_page_match.group(1)) if current_page_match else 1

            # 定义总页数
        total_pages = 26

            # 构造下一页 URL 并请求
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




    def parse_detail(self, response, **kwargs):
        #从meta中获取列表页传递的基础数据
        base_item = response.meta.get('base_item',KaifuspiderItem())
        item = base_item

        # 9.爬取博客正文（静态
        content_div = response.xpath('//div[@id="sina_keyword_ad_area2"]').extract_first()
        if content_div:
            # 使用正则表达式清理HTML标签
            cleanr = re.compile(r'<.*?>')
            cleantext = re.sub(cleanr, '', content_div)
            # 清理空白字符
            cleantext = re.sub(r'\s+', ' ', cleantext).strip()
            item['content'] = cleantext
        else:
            self.logger.warning(f'详情页未找到正文容器，URL: {response.url}')
            item['content'] = ''

        try:
            # 访问详情页获取动态数据
            self.driver.get(response.url)
            time.sleep(3)  # 延长等待时间确保加载完成

            # 10.爬取喜欢数
            like_element = self.driver.find_element(By.XPATH, '//div[@class="upBox upBox_click"]/p[@class="count"]')
            like = like_element.text.strip()
            item['like_count'] = int(like) if like.isdigit() else 0

            # 11.爬取赠金笔数量
            gold_pan_element = self.driver.find_element(By.ID, 'goldPan-num')
            gold_pan_count = gold_pan_element.text.strip()
            item['goldPan'] = int(gold_pan_count) if gold_pan_count.isdigit() else 0

        except Exception as e:
            self.logger.error(f"详情页动态数据爬取失败: {str(e)}，URL: {response.url}")
            item['like_count'] = 0
            item['goldPan'] = 0


        yield item
