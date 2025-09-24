import requests
from bs4 import BeautifulSoup
import csv
import time

# 目标网址（李开复博客首页）
BASE_URL = "http://blog.sina.com.cn/s/articlelist_1191258123_0_{}.html"

# 设置请求头（模拟浏览器防止被拒绝）
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

# 保存到 CSV 文件
csv_file = open("kaifu_blog.csv", "w", newline="", encoding="utf-8-sig")
writer = csv.writer(csv_file)
writer.writerow(["标题", "时间", "正文", "URL"])  # 表头

# 爬取前 5 页文章（每页大概 50 篇，可以调大，比如 range(1, 10)）
for page in range(1, 6):
    url = BASE_URL.format(page)
    print(f"正在抓取第 {page} 页: {url}")

    # 请求目录页
    resp = requests.get(url, headers=headers)
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "lxml")

    # 获取文章链接列表
    links = soup.select(".articleList .atc_title a")
    for link in links:
        article_url = link["href"]

        try:
            # 请求详情页
            detail_resp = requests.get(article_url, headers=headers)
            detail_resp.encoding = "utf-8"
            detail_soup = BeautifulSoup(detail_resp.text, "lxml")

            # 提取数据
            title = detail_soup.select_one(".h1_tit").get_text(strip=True) if detail_soup.select_one(".h1_tit") else "无标题"
            time_str = detail_soup.select_one(".time.SG_txtc").get_text(strip=True) if detail_soup.select_one(".time.SG_txtc") else "无时间"
            content = detail_soup.select_one("#sina_keyword_ad_area2").get_text(strip=True) if detail_soup.select_one("#sina_keyword_ad_area2") else "无正文"

            # 写入 CSV
            writer.writerow([title, time_str, content, article_url])
            print("成功抓取：", title)

            time.sleep(1)  # 防止爬太快被封

        except Exception as e:
            print("抓取失败：", article_url, e)

csv_file.close()
print("爬取完成！数据已保存到 kaifu_blog.csv")
