from __future__ import unicode_literals, print_function, division
from io import open
import re
from pickle import dump
from unicodedata import normalize
import pickle
import pandas as pd
import string
import sys


# load doc into memory
def load_doc(filename, col):
    # open the file
    df = pd.read_csv(filename, sep='\t', header=None)
    text = ""
    for i in range(df[col].size):
        line = str(df[col][i])
        text += line + "\n"
    return text


# split a loaded document into sentences
def to_sentences(doc):
    return doc.strip().split('\n')


# clean a list of lines
def clean_lines(lines):
    cleaned = list()
    # prepare regex for char filtering
    re_print = re.compile('[^%s]' % re.escape(string.printable))
    # prepare translation table for removing punctuation
    table = str.maketrans('', '', string.punctuation)
    for line in lines:
        # normalize unicode characters
        line = normalize('NFD', line).encode('ascii', 'ignore')
        line = line.decode('UTF-8')
        # tokenize on white space
        line = line.split()
        # convert to lower case
        line = [word.lower() for word in line]
        # remove punctuation from each token
        line = [word.translate(table) for word in line]
        # remove non-printable chars form each token
        line = [re_print.sub('', w) for w in line]
        # remove tokens with numbers in them
        line = [word for word in line if word.isalpha()]
        # store as string
        cleaned.append(' '.join(line))
    return cleaned


# save a list of clean sentences to file
def save_clean_sentences(sentences, filename):
    dump(sentences, open(filename, 'wb'))
    print('Saved: %s' % filename)


def load_data(filename):
    lang1 = filename.split('.')[-2][:2]
    lang2 = filename.split('.')[-2][3:]

    print(f"Loading {lang1} data")
    # load Language 1 data
    doc = load_doc(filename, 0)
    sentences = to_sentences(doc)
    sentences = clean_lines(sentences)
    save_clean_sentences(sentences, f'data/{lang1}_{lang1}-{lang2}.pkl')
    # spot check
    print("Some example sentences")
    for i in range(10):
        print(sentences[i])

    print(f"Loading {lang2} data")
    doc = load_doc(filename, 1)
    sentences = to_sentences(doc)
    sentences = clean_lines(sentences)
    save_clean_sentences(sentences, f'data/{lang2}_{lang1}-{lang2}.pkl')
    # spot check
    print("Some example sentences")
    for i in range(10):
        print(sentences[i])

    return lang1, lang2


def write_data(lang1_name, lang2_name):
    with open(f'data/{lang1_name}_{lang1_name}-{lang2_name}.pkl', 'rb') as f:
        fr_voc = pickle.load(f)

    with open(f'data/{lang2_name}_{lang1_name}-{lang2_name}.pkl', 'rb') as f:
        eng_voc = pickle.load(f)

    data = pd.DataFrame(zip(eng_voc, fr_voc), columns=['English', 'French'])
    data.to_csv(f'data/{lang1_name}-{lang2_name}.txt', header=False, index=False, sep='\t')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        lang_1_name, lang_2_name = load_data(filepath)
        write_data(lang_1_name, lang_2_name)
