import article_crawl as ac
from multiprocessing.pool import Pool
from links_crawler import links_crawler

def main(item):
    ac.set_cookie("SUV=003E470174F602035C0F4837D676D579; IPLOC=CN5301; SUID=37A6DDDE3220910A00000000600D4C8A; ABTEST=0|1611484306|v1; ld=vlllllllll2kRUhylllllpl5eiylllllTHLu2Zllll9lllllpklll5@@@@@@@@@@; LCLKINT=7352; LSTMV=212,78; weixinIndexVisited=1; SNUID=F7F39FEC323789B16B055C803353E0A7; JSESSIONID=aaa7-u0EQXjW5esYC0TDx")

    sogou_title, sogou_link = item
    ac.save_one(sogou_title, sogou_link)


if __name__ == '__main__':
    pool = Pool()
    links = links_crawler()
    links.set_keyword("互联网金融")
    links.set_cookie(
    "SUV=003E470174F602035C0F4837D676D579; IPLOC=CN5301; SUID=37A6DDDE3220910A00000000600D4C8A; ABTEST=0|1611484306|v1; ld=vlllllllll2kRUhylllllpl5eiylllllTHLu2Zllll9lllllpklll5@@@@@@@@@@; LCLKINT=7352; LSTMV=212,78; weixinIndexVisited=1; SNUID=F7F39FEC323789B16B055C803353E0A7; JSESSIONID=aaa7-u0EQXjW5esYC0TDx"
    )
    links_dict = links.get_all_links()
    print('+'*100)
    print("links DONE!")
    print('+'*100)

    pool.map(main, links_dict.items())
    pool.close()
    pool.join()
