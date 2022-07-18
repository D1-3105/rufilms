import numpy as np
from nltk import edit_distance
from .models import Phrases
from .serializers import PhraseSerializer

PREPS=(',','.','!','?','\'','"','\n')
SYSTEM_NAMES=('plug', 'greeting')  # this schemes are avoided


def get_phrases():  # count queryset
    big_dict={}
    for phrase in gain_phrases():
        ser=PhraseSerializer(instance=phrase)  # get json from serializer layer
        big_dict.update(ser.data)
    return big_dict


def gain_phrases():
    query_node=Phrases.objects.all()
    for node in SYSTEM_NAMES:
        query_node=query_node.exclude(topic=node)
    return query_node


def get_plug():  # count plugs-> plugs should exist
    return Phrases.objects.filter(topic='plug').first().pk  # count plug ONLY FIRST PLUG CAN BE REACHED


def delete_delim(word:str):  # erase all delimiters from word  ( ?w,->w )
    new_word=''
    for sym in list(word):
        if sym not in PREPS:
            new_word+=sym
    return new_word


def detect_scheme(text:str):
    text=text.lower()  # all words -> lower keys
    schemes = np.array(list(get_phrases().keys()))  # key phrases
    phrases_context = np.array(list(get_phrases().items()), dtype=object)  # key phrases with topic
    no_tails=np.array([delete_delim(i)
                       for i in text.split()
                       if i[0].isalnum() and len(i)>1]
                      )  # text with no short words
    phrases_matrix=np.zeros(len(schemes))  # frequency of topics
    for wordpos, word in enumerate(no_tails):
        for pos, context in enumerate(phrases_context):
            scheme, phrases = context
            for phrase in phrases:
                word_buffer=word  # window of words
                if len(phrase.split(' '))>1:  # means phrase consists of 2 words
                    word_buffer=' '.join(w for w in
                                 no_tails[wordpos+1:(wordpos+len(phrase.split(' '))+1)
                                 if wordpos+len(phrase.split(' '))+1 else len(no_tails)])
                                 # we should watch window+next word
                if edit_distance(phrase, word_buffer)<(len(word_buffer)*0.5):
                    print(word_buffer, phrase, edit_distance(phrase, word_buffer), len(word_buffer)*0.5, sep='/')
                    phrases_matrix[pos]+=1  # [0,0,0]->[0,1,0]
                    break
    if len(schemes)>0:
        answer=schemes[phrases_matrix.argmax()]  # numpy method to calculate max arg in matrix
    if len(schemes)==0 or max(phrases_matrix)==0:  # no calculated schemes -> get plug
        answer=get_plug()  # pk of plug phrase
    return answer  # pk of phrase

