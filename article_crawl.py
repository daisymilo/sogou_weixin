import requests
import re
from lxml import etree
from selenium import webdriver
from datetime import datetime, timedelta
import os
import duplicate_check as dc

print("article_crawl模块：请先调用set_cookie(<cookie字符串>)方法更改cookie,cookie值与links_crawler模块相同")
print("article_crawl模块：调用set_path可以设置保存路径，填入绝对路径字符串，默认保存路径：")
print("当前Python脚本所在目录/爬取结果/")
print('+'*100)

USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 " \
             "Safari/535.1 "
COOKIE_FOR_SOGOU = "SUV=003E470174F602035C0F4837D676D579; IPLOC=CN5301; SUID=37A6DDDE3220910A00000000600D4C8A; " \
                   "ABTEST=0|1611484306|v1; ld=vlllllllll2kRUhylllllpl5eiylllllTHLu2Zllll9lllllpklll5@@@@@@@@@@; " \
                   "LCLKINT=7352; LSTMV=212,78; weixinIndexVisited=1; SNUID=80279EDD6B69D1CE821C95866CE484C9 "
SAVE_PATH = "./爬取结果/"
HEADERS = {'User-Agent': USER_AGENT,
           'Cookie': COOKIE_FOR_SOGOU
           }


def set_path(path):
    global SAVE_PATH
    SAVE_PATH = path
    print("设置保存路径成功!")


def set_cookie(cookie):
    global COOKIE_FOR_SOGOU
    global HEADERS
    COOKIE_FOR_SOGOU = cookie
    HEADERS = {'User-Agent': USER_AGENT,
               'Cookie': COOKIE_FOR_SOGOU
               }


def init_webdriver():
    """
    初始化一个webdriverChrome
    :return: 浏览器对象
    """
    # 初始化webdriver
    options = webdriver.ChromeOptions()
    # 以无界面模式启动
    options.add_argument("--headless")
    # 更改User-Agent
    options.add_argument(
        "user-agent='Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1'")
    # 禁止在状态栏显示正在被自动化控制的信息
    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    # 禁止Chrome带有正在被自动化控制的信息
    options.add_argument("--disable-blink-features=AutomationControlled")
    browser = webdriver.Chrome(options=options)
    return browser


def get_weixin_link(sogou_link):
    '''
   将通过搜狗原始链接获得文章的真实链接
   :param sogou_link: 通过搜狗获得的文章原始链接
   :return: 文章真实链接
   '''

    regex = "url \+= '(.*?)';"
    source_link = requests.get(sogou_link, headers=HEADERS).text
    weixin_link = ''.join(re.findall(regex, source_link))
    return weixin_link


def get_page_source(sogou_link):
    '''
    获取文章页面源代码
    :param sogou_link: 文章原始链接(搜狗链接)
    :return: 文章页面源代码
    '''
    browser = init_webdriver()
    weixin_link = get_weixin_link(sogou_link)
    browser.get(weixin_link)
    page_source = browser.page_source
    browser.close()
    return page_source


def time_parser(time_str):
    '''
   将表述时间的词语转换为日期
   :param time_str: 表述时间的词语
   :return： 日期字符串YYYY-MM-DD
   '''

    time_format = "%Y-%m-%d"
    try:
        if time_str == "今天":
            time = datetime.strftime(datetime.now(), time_format)
        elif time_str == "昨天":
            time = datetime.strftime(datetime.now() - timedelta(days=1), time_format)
        elif time_str == "前天":
            time = datetime.strftime(datetime.now() - timedelta(days=2), time_format)
        elif time_str == "一周前":
            time = datetime.strftime(datetime.now() - timedelta(days=7), time_format)
        elif time_str == "1周前":
            time = datetime.strftime(datetime.now() - timedelta(days=7), time_format)
        elif "天前" in time_str:
            days = int(time_str[0])
            time = datetime.strftime(datetime.now() - timedelta(days=days), time_format)
        else:
            regex = "(\d+)月(\d+)日"
            res = re.search(regex, time_str)
            month = int(res.group(1))
            day = int(res.group(2))
            time = datetime.strftime(datetime(2021, month, day), time_format)
    except:
        time = time_str
    return time


def get_article_info(sogou_title, page_source):
    '''
    获取文章的一些基本信息
    :sogou_title: 爬取搜狗链接时获得的文章标题
    :param page_source: 文章页面源代码
    :return: 文章标题，原创标签，作者名称，公众号名称，发布时间
    '''
    html = etree.HTML(page_source)
    try:
        origin = html.xpath("//span[@id='copyright_logo']/text()")[0]
    except:
        origin = "非原创"
    try:
        author = html.xpath("//span[@id='js_author_name']/text()")[0]
    except:
        author = "--作者未提供--"
    try:
        publisher = html.xpath("//strong[@class='profile_nickname']/text()")[0]
    except:
        publisher = "--公众号未提供--"
    try:
        time_str = html.xpath("//em[@id='publish_time']/text()")[0]
        time = time_parser(time_str)
    except:
        time = "--时间未知--"
        page_save_path = SAVE_PATH + "该文章网页源代码有误_" + sogou_title + ".txt"
        with open(page_save_path, 'w', encoding='utf-8') as f:
            f.write(page_source)
    article_info = [sogou_title, origin, author, publisher, time]
    return article_info


def get_full_article(page_source):
    '''
    获取正文全文
    :page_source: 文章页面源代码
    :return: 列表形式文章全文
    '''
    html = etree.HTML(page_source)
    text_list = []
    for text in html.xpath("//div[@class='rich_media_content ']//text()"):
        clean_text = text.replace(' ', '').replace('\n', '')
        if clean_text:
            text_list.append(clean_text)
    return text_list


def file_path_check(article_info):
    '''
    检查路径是否存在
    :param article_info: 文章的标题，原创，作者，公众号，发布时间信息:
    :return: 文件保存路径
    '''
    if not os.path.exists(SAVE_PATH):
        os.mkdir(SAVE_PATH)
    SAVE_PATH_ONE = SAVE_PATH + datetime.strftime(datetime.now(),"%Y-%m-%d") + "/"
    if not os.path.exists(SAVE_PATH_ONE):
        os.mkdir(SAVE_PATH_ONE)
    file_path = SAVE_PATH_ONE + "_".join(article_info) + ".txt"
    if not os.path.exists(file_path):
        return file_path
    else:
        return ''


def save_as_txt(article_info, text_list):
    '''
    将全文保存为txt文档
    :param article_info: 文章信息
    :param text_list: 文章全文
     '''
    file_path = file_path_check(article_info)
    if file_path:
        with open(file_path, 'w', encoding='utf-8') as f:
            for line in text_list:
                f.write(line)
                f.write('\n')
        print(file_path)
    else:
        print("文件已存在!")


def save_one(sogou_title, sogou_link):
    '''
    保存一篇文章
    :param sogou_title: 搜狗文章标题
    :param sogou_link: 搜狗文章链接
    '''
    page_source = get_page_source(sogou_link)
    article_info = get_article_info(sogou_title, page_source)
    text_list = get_full_article(page_source)
    if dc.duplicate_check(text_list):
        save_as_txt(article_info, text_list)