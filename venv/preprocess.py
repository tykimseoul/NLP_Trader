import pandas as pd
import matplotlib.pyplot as plt
from konlpy.tag import Kkma
import nltk
import re
import datetime

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 2000)
pd.set_option('display.max_colwidth', 200)
pd.set_option('display.max_rows', None)


def sent_tokenize(text):
    text = re.sub(r'\s+', ' ', text)
    sents = nltk.sent_tokenize(text)
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
    try:
        date_string = nltk.word_tokenize(result[-1])[0]
        if datetime.datetime.strptime(date_string, '%Y.%m.%d'):
            result = result[:-1]
    except ValueError:
        pass
    result = list(filter(lambda s: not re.match(r'.+@.+\..+', s), result))
    result = list(filter(lambda s: not re.match(r'.*ⓒ.*', s), result))
    if len(result) == 0:
        return None
    print(result)
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


dfo = pd.read_csv('./output_20200826.csv')
dfo.dropna(inplace=True)
dfo['len'] = dfo.apply(lambda r: len(str(r['content'])), axis=1)
dfo.sort_values('len', inplace=True, ascending=True)
dfo.drop(dfo[dfo['len'] > 6000].index, inplace=True)
dfo.reset_index(inplace=True, drop=True)
dfo['cumsum'] = dfo['len'].cumsum()
print(dfo.head(100))

kkma = Kkma()
df = pd.read_csv('./output_20200826.csv')
df.dropna(inplace=True)
df['sents'] = df.apply(lambda r: sent_tokenize(r['content']), axis=1)
df['sents_stripped'] = df.apply(lambda r: strip_sent(r['sents']), axis=1)
df.dropna(inplace=True)
df['len'] = df['sents_stripped'].str.join(' ').str.len()
df['sent_count'] = df.apply(lambda r: len(r['sents_stripped']), axis=1)
df.sort_values('len', inplace=True, ascending=True)
df.reset_index(inplace=True, drop=True)
df.drop(df[df['sent_count'] < 2].index, inplace=True)
df.drop(df[df['len'] > 6000].index, inplace=True)
print(df.head(200))
df['cumsum'] = df['len'].cumsum()

dfo['cumsum'].plot()
df['cumsum'].plot()
plt.show()
dfo['len'].hist(bins=100)
df['len'].hist(bins=100, alpha=0.7)
plt.show()