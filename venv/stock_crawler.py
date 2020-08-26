import pandas as pd
import os
from dotenv import load_dotenv
import json
import requests
from bs4 import BeautifulSoup
import time

load_dotenv()


def get_html(url, t):
    print(url)
    try:
        return requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    except requests.exceptions.ConnectionError:
        print('pausing for {}'.format(url))
        time.sleep(t)
        return get_html(url, t + 5)


def parse_stock_table(code, last_page):
    dfs = []
    for page in range(1, last_page + 1):
        print(code, page)
        df = pd.read_html(os.getenv("DAILY_DATA_SOURCE_ADDRESS").format(code=code, page=page))[0]
        df.dropna(inplace=True)
        dfs.append(df)
        time.sleep(0.1)
    full_df = pd.concat(dfs)
    full_df.reset_index(inplace=True, drop=True)
    full_df.to_csv('./stock_data_{}.csv'.format(code))
    print(full_df.head(20))


codes = json.loads(os.getenv("RELEVANT_STOCK_CODES"))
for code in codes:
    html = get_html(os.getenv("DAILY_DATA_SOURCE_ADDRESS").format(code=code, page=10000), 5)
    document = BeautifulSoup(html.text, "html.parser")
    last_page = int(document.select_one('.on').text.strip())
    print(last_page)
    parse_stock_table(code, last_page)
