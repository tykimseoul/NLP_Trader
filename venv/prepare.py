from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.utils import to_categorical
import pandas as pd
import ast
from collections import Counter
import os
import numpy as np
from datetime import datetime, date, timedelta


def encode_stock_data(code):
    stock_file = './stock_data/stock_data_{}.csv'.format(code)
    df = pd.read_csv(stock_file, index_col=0)
    df.reset_index(drop=True, inplace=True)
    df['종가'] = df['종가'].astype(float)
    df['변화율'] = df['종가'].pct_change(periods=-1, axis=0, fill_method='bfill')
    df['변화율'] = df.apply(lambda r: 0 if abs(r['변화율']) < 0.001 else r['변화율'] / abs(r['변화율']), axis=1)
    df.dropna(inplace=True)
    df['변화율'] = df['변화율'].astype(int)
    df['encoding'] = df.apply(lambda r: np.array(to_categorical(r['변화율'], num_classes=3)), axis=1)
    print(df.head())
    return df[['날짜', 'encoding']]


full_df = encode_stock_data('017670')
dates = full_df['날짜'].tolist()
dates.append(None)
date_pairs = list(zip(dates[1:], dates[:-1]))

news_path = './processed/'

vocab_size = 50000
tokenizer = Tokenizer(num_words=vocab_size)
morpheme_size = 500
morpheme_data = {}


def fit_tokenizer(tokenizer):
    morphemes = []
    for file in sorted(os.listdir(news_path), reverse=True):
        news_file = news_path + file

        df = pd.read_csv(news_file)
        df = df.sample(min(5000, len(df)))
        df['morphemes'] = df.apply(lambda r: list(ast.literal_eval(r['morphemes'])), axis=1)
        df['morphemes'] = df.apply(lambda r: list(map(str, r['morphemes']))[:morpheme_size], axis=1)
        x_data = df['morphemes'].tolist()
        morpheme_data[file] = x_data
        morphemes.extend(x_data)

    tokenizer.fit_on_texts(morphemes)
    print(tokenizer.word_counts)
    return tokenizer


tokenizer = fit_tokenizer(tokenizer)


def prepare_data():
    y_train = []
    x_train = []
    for file in sorted(os.listdir(news_path), reverse=True):
        print(file)
        news_date = datetime.strptime(file, '%Y%m%d.csv')
        stock_date = None
        for pair in date_pairs:
            first = datetime.strptime(pair[0], '%Y.%m.%d')
            second = datetime.strptime(pair[1], '%Y.%m.%d')
            if first <= news_date < second:
                stock_date = second
                break

        x_data = morpheme_data[file]
        x_data = tokenizer.texts_to_sequences(x_data)
        x_data = pad_sequences(x_data, maxlen=morpheme_size)
        print(x_data.shape)
        x_train.append(x_data)

        stock_data = full_df[full_df['날짜'] == stock_date.strftime('%Y.%m.%d')]
        stock_data = stock_data.drop(['날짜'], axis=1)
        stock_data = np.array(stock_data.values.tolist())
        stock_data = np.concatenate(stock_data, axis=None)
        print(stock_data)
        y_train.append(np.tile(stock_data, (len(x_data), 1)))

    x_train = np.concatenate(x_train)
    print(x_train.shape)
    y_train = np.concatenate(y_train)
    print(y_train.shape)

    np.save('x_train.npy', x_train)
    np.save('y_train.npy', y_train)


prepare_data()
