from news_crawler import *
import os
import pandas as pd
from datetime import datetime, date, timedelta
from tzlocal import get_localzone
from pytz import timezone
import schedule


def parse_post(url, category, raw):
    document = BeautifulSoup(raw, "lxml")
    title = document.select_one('.article_info > #articleTitle').text
    if re.match(r'^[0-9a-zA-Z\s]+$', title):
        return None
    date = document.select_one('.article_info > .sponsor > .t11').text
    article = document.select_one('.article_body > #articleBodyContents')
    if article is None:
        return None
    for s in article.find_all(['script', 'strong']) \
             + article.select('.end_photo_org') \
             + article.select('font > table') \
             + article.select('.vod_area'):
        s.extract()
    for element in article(text=lambda text: isinstance(text, Comment)):
        element.extract()
    content = article.findAll(text=True, recursive=True)
    content = list(filter(lambda c: c not in ['\n', ' ', '\t'], content))
    content = list(map(lambda c: c.strip(), content))
    content = ' '.join(content)
    dct = {'title': title, 'date': date, 'category': category, 'content': content, 'url': url}
    return dct


def parse_every_night():
    raw_path = './raw/'
    raw_files = set(os.listdir(raw_path))
    parsed_path = './parsed/'
    parsed_files = set(os.listdir(parsed_path))
    parsing = raw_files - parsed_files
    for f in parsing:
        print('Parsing {}'.format(f))
        df = pd.read_csv(raw_path + f)
        df['temp'] = df.apply(lambda r: parse_post(str(r['url']), r['category'], r['raw']), axis=1)
        df = pd.io.json.json_normalize(df.temp)
        df.to_csv(parsed_path + f)


if __name__ == "__main__":
    print("Starting news parsing..")
    schedule.every(4).hours.do(parse_every_night)

    while True:
        schedule.run_pending()
        time.sleep(1)
