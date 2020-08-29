import requests
from bs4 import BeautifulSoup, Comment
from datetime import datetime, date, timedelta
from tzlocal import get_localzone
import time
import pandas as pd
import re
from pytz import timezone
import schedule

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 200)
pd.set_option('display.max_rows', None)

categories = {'politics': 100, 'economy': 101, 'society': 102, 'culture': 103, 'world': 104, 'science': 105, 'opinion': 110}

base_url = 'https://news.naver.com/main/list.nhn?mode=LSD&mid=shm&sid1={}&date={}&page={}'


def get_html(url, t):
    print(url)
    time.sleep(1)
    try:
        return requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    except requests.exceptions.ConnectionError:
        print('pausing for {}'.format(url))
        time.sleep(t)
        return get_html(url, t + 5)


def parse_category(category, date):
    html = get_html(base_url.format(category, date, 10000), 5)
    document = BeautifulSoup(html.text, "html.parser")
    last_page = document.select_one('.paging > strong').text
    print(last_page)
    return int(last_page)


def parse_post_list(category, date, last_page):
    links = []
    for i in range(1, last_page + 1):
        html = get_html(base_url.format(category, date, i), 5)
        page = BeautifulSoup(html.text, "html.parser")
        post_temp = page.select('.newsflash_body > .type06_headline > li > dl > dt > a')
        links.extend(list(set(map(lambda p: p.get('href'), post_temp))))
    return links


def raw_post(url, category):
    html = get_html(url, 5)
    if html.url != url:
        return None
    dct = {'url': url, 'category': category, 'raw': html.text}
    return dct


def crawl_every_night():
    now = datetime.now().astimezone(timezone('Asia/Seoul'))
    full_string = now.strftime('%Y%m%d%H%M%S')
    date_string = now.strftime('%Y%m%d')
    print("Initiating crawling: {d}".format(d=full_string))
    start = time.time()
    dfs = []
    for category in categories.values():
        last_page = parse_category(category, date_string)
        posts = parse_post_list(category, date_string, last_page)
        print(len(posts))
        data = list(map(lambda p: raw_post(p, category), posts))
        df = pd.DataFrame(data)
        print(df.head())
        dfs.append(df)
    full_df = pd.concat(dfs)
    full_df.reset_index(inplace=True, drop=True)
    full_df.to_csv('./raw/{}.csv'.format(date_string))
    end = time.time()
    print("Crawling complete: {t}".format(t=time.strftime("%H:%M:%S", time.gmtime(end - start))))


if __name__ == "__main__":
    print("Starting news crawling..")
    korea_time = timezone('Asia/Seoul').localize(datetime(2020, 1, 1, 23, 50, 0))
    local_time = korea_time.astimezone(get_localzone()).time().strftime('%H:%M')
    schedule.every().day.at(local_time).do(crawl_every_night)

    while True:
        schedule.run_pending()
        time.sleep(1)
