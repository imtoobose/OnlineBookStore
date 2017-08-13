from collections import Counter 
from random import randint
from math import log, floor
import string
from operator import itemgetter
import os
import pickle

def chunk_load(f, chunk_size=1024):
    while True:
        text = f.read(chunk_size)
        if not text:
            break
        yield text

def get_nlp_features(book_path, nlp):
    with open(os.path.join(book_path, 'meta.pkl'),'rb') as f:
        m = pickle.load(f)
        arr = m['chapters']
        verbcount = list()
        people = list()
        book_name = m['title'] 

        for chap in arr:
            count = 0
            text_word_len = 0

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

    return verbcount, Counter(people)