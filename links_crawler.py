import requests
import time
from lxml import etree

KEYWORD = "互联网金融"
USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1"
COOKIE = ""


class links_crawler(object):
    def __init__(self):
        self.keyword = KEYWORD
        self.base_url = "https://weixin.sogou.com/weixin?query={}&type=2".format(self.keyword)
        self.user_agent = USER_AGENT
        self.cookie = COOKIE
        print("links_crawler模块：请先访问以下网址获取cookie，调用self.set_cookie更改cookie：")
        print(self.base_url)
        print("links_crawler模块：调用self.set_keyword以更改搜索关键词")
        print('+'*100)

    def get_page(self, url):
        '''
        用于获取一个页面的源代码
        :param url: 页面的链接
        :return: 网页源代码
        '''
        headers = {
            'User-Agent': self.user_agent,
            'Cookie': self.cookie
        }
        response = requests.get(url, headers=headers)
        return response.text

    def get_article_links(self, html):
        '''
        用于解析出一个搜索结果页面中的所有公众号链接和标题
        :param html:网页源代码
        :return:文章标题和链接的生成器
        '''
        html = etree.HTML(html)
        lis = html.xpath("//ul[@class='news-list']/li")
        for li in lis:
            title_raw = ''.join(li.xpath("./div[@class='txt-box']/h3/a[@target='_blank']//text()"))
            title = title_raw.replace('/', '').replace('\\', '').replace(':', '').replace('*', '').replace('"',
                                                                                                           '').replace(
                '<', '').replace('>', '').replace('|', '').replace('?', '')
            link = 'https://weixin.sogou.com' + li.xpath("./div[@class='txt-box']/h3/a[@target='_blank']/@href")[0]
            yield title, link

    def get_next_page(self, html):
        '''
        用于解析出下一页的链接
        :param html:网页源代码
        :return:下一页链接
        '''
        html = etree.HTML(html)
        path = html.xpath("//div[@class='p-fy']/a[@id='sogou_next']/@href")[0]
        next_page = "https://weixin.sogou.com/weixin" + path
        return next_page

    def get_all_links(self):
        links_dict = {}
        url = self.base_url
        while True:
            html = self.get_page(url)
            for title, link in self.get_article_links(html):
                links_dict.setdefault(title, link)
            try:
                url = self.get_next_page(html)
            except IndexError:
                break
            time.sleep(1)
        return links_dict

    def set_cookie(self, cookie):
        '''
        设置cookie
        :param cookie: cookie字符串
        '''
        self.cookie = cookie

    def set_keyword(self, keyword):
        '''
        设置搜索关键词
        :param keyword: 搜索关键词
        '''
        self.keyword = keyword
        self.base_url = "https://weixin.sogou.com/weixin?query={}&type=2".format(self.keyword)
        print('搜索关键词：',self.keyword)
