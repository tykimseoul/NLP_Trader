from news_crawler import *

now = datetime.now().astimezone(timezone('Asia/Seoul'))
while True:
    now = now - timedelta(days=1)
    full_string = now.strftime('%Y%m%d%H%M%S')
    date_string = now.strftime('%Y%m%d')
    print("Initiating crawling: {d}".format(d=full_string))
    start = time.time()
    dfs = []
    for category in categories.values():
        last_page = parse_category(category, date_string)
        posts = parse_post_list(category, date_string, last_page)
        print(len(posts))
        data = list(map(lambda p: parse_post(p, category), posts))
        data = list(filter(lambda p: p is not None, data))
        df = pd.DataFrame(data)
        print(df.head())
        dfs.append(df)
    full_df = pd.concat(dfs)
    full_df.reset_index(inplace=True, drop=True)
    full_df.to_csv('./news_data/{}.csv'.format(date_string))
    end = time.time()
    print("Crawling complete: {t}".format(t=time.strftime("%H:%M:%S", time.gmtime(end - start))))
