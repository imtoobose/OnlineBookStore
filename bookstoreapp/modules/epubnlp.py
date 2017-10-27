from collections import Counter 
from random import randint
from math import log, floor
import string
from operator import itemgetter
import os
import pickle
import matplotlib.pyplot as plt

def chunk_load(f, chunk_size=1024):
    while True:
        text = f.read(chunk_size)
        if not text:
            break
        yield text

def get_nlp_features(book_path, nlp, plot=False):
    excluded_chapters = ['COPYRIGHT', 'TITLE', 'INDEX', 'ACKNOWLEDGMENTS', 
                        'APPENDIX', 'PREFACE', 'COVER']
    with open(os.path.join(book_path, 'meta.pkl'),'rb') as f:
        m = pickle.load(f)
        arr = m['chapters']
        verbcount = list()
        people = list()
        book_name = m['title'] 

        for chap in arr:
            count = 0
            text_word_len = 0

            if chap['chapname'].upper() in excluded_chapters:
                continue

            with open(os.path.join(book_path, chap['filename']), 'r') as f:
                for chunk in chunk_load(f):
                    text = nlp(chunk)
                    text_word_len += len(text)

                    for w in text:
                        count += int(w.pos_ == 'VERB')

                    for ent in text.ents:
                        if ent.label_ == 'PERSON':
                            people.append(ent.text)

                    del text

            
            if count > 30:
                verbcount.append({'chap': chap['chapname'], 
                                  'count': count/text_word_len})

    if plot:
        x = [y for y in range(0, len(verbcount))]
        y = [xx['count'] for xx in verbcount]
        ticks = [xx['chap'] for xx in verbcount]
        plt.plot(x, y, linestyle='-', marker='o')
        if not book_name == None:
            plt.title(book_name)

        plt.xticks(x, ticks, rotation='vertical')
        plt.xlabel('Chapter')
        plt.ylabel('Normalized Verb Count')
        plt.tick_params(axis='both', which='major', labelsize=8)
        plt.tight_layout()
        plt.show()

    return verbcount, Counter(people)