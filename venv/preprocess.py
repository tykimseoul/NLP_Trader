import pandas as pd
import matplotlib.pyplot as plt
from konlpy.tag import Kkma
import nltk
import re
import datetime

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
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


kkma = Kkma()
df = pd.read_csv('./output_20200826.csv')
df.dropna(inplace=True)
df['len'] = df.apply(lambda r: len(str(r['content'])), axis=1)
df['sents'] = df.apply(lambda r: sent_tokenize(r['content']), axis=1)
df['sents_stripped'] = df.apply(lambda r: strip_sent(r['sents']), axis=1)
df.dropna(inplace=True)
df['sent_count'] = df.apply(lambda r: len(r['sents_stripped']), axis=1)
df.sort_values('sent_count', inplace=True, ascending=True)
df.reset_index(inplace=True, drop=True)
df.drop(df[df['sent_count'] < 2].index, inplace=True)
df.drop(df[df['len'] > 6000].index, inplace=True)
print(df.head(200))
df['cumsum'] = df['len'].cumsum()
df['prp'] = df['cumsum'] / max(df['cumsum'])
# df['cumsum'].plot()
df['sent_count'].hist(bins=100)
print(df.head())
plt.show()
