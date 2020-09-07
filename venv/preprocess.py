#!/usr/bin/python
# -*- coding: <utf-8> -*-
import pandas as pd
import matplotlib.pyplot as plt
from konlpy.tag import Kkma, Okt, Komoran, Hannanum
import kss
import nltk
import re
import datetime
from collections import Counter
import os

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 2000)
pd.set_option('display.max_colwidth', 200)
pd.set_option('display.max_rows', None)

josa = '(' + ')|('.join(['JK[A-Z]', 'JX', 'JC']) + ')'
eomi = '(' + ')|('.join(['E[A-Z]+', 'X[A-Z]+']) + ')'
symbol = '(' + ')|('.join(['S[A-Z]']) + ')'


def sent_tokenize(text):
    text = re.sub(r'\s+', ' ', text)
    sents = kss.split_sentences(text)
    return sents


def strip_sent(sents):
    result = sents[:-1]
    if len(result) == 0:
        return None
    try:
        result[0] = remove_header(result[0])
    except RecursionError:
        return None
    try:
        if nltk.word_tokenize(result[0])[2] == '=':
            idx = result[0].index('=')
            result[0] = result[0][idx + 1:].strip()
    except IndexError:
        pass
    result = list(filter(len, result))
    if len(result) == 0:
        return None
    for i, s in enumerate(result):
        date_string = nltk.word_tokenize(result[len(result) - i - 1])[0]
        try:
            if datetime.datetime.strptime(date_string, '%Y.%m.%d'):
                result.pop(len(result) - i - 1)
                break
        except ValueError:
            pass
    word_exclusions = "(" + ")|(".join([r'.+@.+\..+', r'.*ⓒ.*', r'.*Copyright.*', r'.*▶.*']) + ")"
    result = list(filter(lambda s: not re.match(word_exclusions, s), result))
    stop_phrases = ['공감언론 뉴시스가 독자 여러분의 소중한 제보를 기다립니다.', '드링킷', '※ \'당신의 제보가 뉴스가 됩니다\' YTN은 여러분의 소중한 제보를 기다립니다.']
    result = list(filter(lambda s: s not in stop_phrases, result))
    if len(result) == 0:
        return None
    # print(result)
    return result


def remove_header(sent):
    try:
        if re.match(r'^[\[(]', sent):
            sent = re.sub(r'^([(\[]).*?([)\]])', '', sent)
            sent = sent.strip()
            return remove_header(sent)
        else:
            return sent
    except RecursionError:
        raise


def extract_morphemes(komoran, sent):
    try:
        morphs = komoran.pos(sent)
    except UnicodeDecodeError:
        return None
    morphs = list(filter(lambda m: not re.match(josa, m[1]) and not re.match(eomi, m[1]) and not re.match(symbol, m[1]), morphs))
    print(morphs)
    return morphs


file_path = './news_data/'

komoran = Komoran()
for news in sorted(os.listdir(file_path)):
    news_file = file_path + news
    df = pd.read_csv(news_file, engine='python')
    df.dropna(inplace=True)
    df.drop_duplicates('content', keep='first', inplace=True)
    df['sents'] = df.apply(lambda r: sent_tokenize(r['content']), axis=1)
    df['sents_stripped'] = df.apply(lambda r: strip_sent(r['sents']), axis=1)
    df.dropna(inplace=True)
    df['content_stripped'] = df['sents_stripped'].str.join(' ')
    df['len'] = df['content_stripped'].str.len()
    df.drop(df[df['len'] > 2000].index, inplace=True)
    df.drop(df[df['len'] < 200].index, inplace=True)
    df.sort_values('len', inplace=True, ascending=False)
    df['morphemes'] = df.apply(lambda r: extract_morphemes(komoran, r['content_stripped']), axis=1)
    df.dropna(inplace=True)
    # df['morph_size'] = df.apply(lambda r: len(r['morphemes']), axis=1)
    # df['freqs'] = df.apply(lambda r: Counter(r['morphemes']).most_common(10), axis=1)
    # df['sent_count'] = df.apply(lambda r: len(r['sents_stripped']), axis=1)
    # df.drop(df[df['sent_count'] < 3].index, inplace=True)
    df.reset_index(inplace=True, drop=True)
    print(df.head(100))
    # df['cumsum'] = df['len'].cumsum()

    df[['title', 'date', 'category', 'morphemes']].to_csv('./processed/' + news)
