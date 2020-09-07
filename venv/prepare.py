from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
import pandas as pd
import ast
from collections import Counter
import os
import numpy as np
from datetime import datetime, date, timedelta

vocab_size = 50000
tokenizer = Tokenizer(num_words=vocab_size)

stock_path = './stock_data/'
stocks = []
for code in os.listdir(stock_path):
    stock_file = stock_path + code
    df = pd.read_csv(stock_file, index_col=0)
    df.reset_index(drop=True, inplace=True)
    if len(stocks) == 0:
        stocks.append(df['날짜'])
    df = df.drop(['날짜', '전일비'], axis=1)
    stocks.append(df)

full_df = pd.concat(stocks, axis=1)
print(full_df.head())
dates = full_df['날짜'].tolist()
dates.append(None)
date_pairs = list(zip(dates[1:], dates[:-1]))
print('pairs', date_pairs)

news_path = './processed/'
news_days = len(os.listdir(news_path))
y_train = []
x_train = []

morphemes = []
for file in sorted(os.listdir(news_path), reverse=True)[:2]:
    news_file = news_path + file

    df = pd.read_csv(news_file)
    df['morphemes'] = df.apply(lambda r: list(ast.literal_eval(r['morphemes'])), axis=1)
    df['morphemes'] = df.apply(lambda r: list(map(str, r['morphemes'])), axis=1)
    x_data = df['morphemes'].tolist()
    morphemes.extend(x_data)

tokenizer.fit_on_texts(morphemes)
print(tokenizer.word_counts)

for file in sorted(os.listdir(news_path), reverse=True)[:2]:
    print(file)
    news_date = datetime.strptime(file, '%Y%m%d.csv')
    stock_date = None
    for pair in date_pairs:
        first = datetime.strptime(pair[0], '%Y.%m.%d')
        second = datetime.strptime(pair[1], '%Y.%m.%d')
        if first <= news_date < second:
            stock_date = second
            break

    news_file = news_path + file

    df = pd.read_csv(news_file)
    df['morphemes'] = df.apply(lambda r: list(ast.literal_eval(r['morphemes'])), axis=1)
    df['morphemes'] = df.apply(lambda r: list(map(str, r['morphemes'])), axis=1)

    x_data = df['morphemes'].tolist()
    x_data = tokenizer.texts_to_sequences(x_data)
    x_data = pad_sequences(x_data, maxlen=500)
    print(x_data.shape)
    x_train.append(x_data)

    stock_data = full_df[full_df['날짜'] == stock_date.strftime('%Y.%m.%d')]
    stock_data = stock_data.drop(['날짜'], axis=1)
    print(stock_data)
    y_train.append(np.tile(stock_data.to_numpy(), (len(df), 1)))

x_train = np.concatenate(x_train)
print(x_train.shape)
y_train = np.concatenate(y_train)
print("sdfsd", y_train.shape)
