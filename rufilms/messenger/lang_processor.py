import numpy as np
from nltk import edit_distance
from .models import Phrases
from itertools import permutations

PREPS=(',','.','!','?','\'','"','\n')
SYSTEM_NAMES=('plug', 'greeting','END OF SCRIPT', 'AUTH PHRASE')  # this schemes are avoided
SCRIPT_ENDER = 'END OF SCRIPT'


class DefaultProcessor:

    def get_phrases(self):  # count queryset
        big_dict={}
        print(self.gain_phrases())
        for phrase in self.gain_phrases():
            data_dict = {
                phrase.pk: sorted(phrase.phrases, key=lambda x: len(x), reverse=True),
            }
            big_dict.update(data_dict)
        return big_dict

    def gain_phrases(self):
        query_node=Phrases.objects.all()
        for node in SYSTEM_NAMES:
            query_node=query_node.exclude(topic=node)
        return query_node

    def get_plug(self):  # count plugs-> plugs should exist
        return Phrases.objects.filter(topic='plug').first().pk  # count plug ONLY FIRST PLUG CAN BE REACHED

    def delete_delim(self,word:str):  # erase all delimiters from word  ( ?w,->w )
        new_word=''
        for sym in list(word):
            if sym not in PREPS:
                new_word+=sym
        return new_word

    @staticmethod
    def count_edit_distance(phrase, word_buffer):
        mutations_phrases=[' '.join(i) for i in list(permutations(phrase.split(), len(phrase.split())))]
        edit_distances = []
        for mini_phrase in mutations_phrases:
            edit_distances.append(edit_distance(mini_phrase, word_buffer))
        return min(edit_distances)

    def detect_scheme(self,text:str):
        text=text.lower()  # all words -> lower keys
        schemes = np.array(list(self.get_phrases().keys()))  # key phrases
        phrases_context = np.array(list(self.get_phrases().items()), dtype=object)  # key phrases with topic

        no_tails=np.array([self.delete_delim(i)
                           for i in text.split()
                           if i[0].isalnum() and len(i)>1]
                          )  # text with no short words
        phrases_matrix=np.array([100]*len(schemes))  # frequency of topics
        for wordpos, word in enumerate(no_tails):
            for pos, context in enumerate(phrases_context):
                scheme, phrases = context
                for phrase in phrases:
                    word_buffer=word  # window of words
                    if len(phrase.split(' '))>1:  # means phrase consists of 2 words
                        word_buffer=' '.join(w for w in
                                     no_tails[wordpos:(wordpos+len(phrase.split(' '))+1)
                                     if wordpos+len(phrase.split(' '))+1 else len(no_tails)])
                                     # we should watch window+next word

                        #print('WB:',word_buffer)
                    if self.count_edit_distance(phrase, word_buffer)<(len(word_buffer)*0.5):
                        print(word_buffer, phrase, self.count_edit_distance(phrase, word_buffer),
                              len(word_buffer)*0.5, sep='/')
                        phrases_matrix[pos]=self.count_edit_distance(phrase, word_buffer)  # [0,0,0]->[0,1,0]
                        break
        answer=None
        if len(schemes)>0:
            answer=schemes[phrases_matrix.argmin()]  # numpy method to calculate max arg in matrix
        if len(schemes)==0 or min(phrases_matrix)==100:  # no calculated schemes -> get plug
            answer=self.get_plug()  # pk of plug phrase
        return answer  # pk of phrase


class ScriptProcessor(DefaultProcessor):

    def gain_phrases(self):
        return Phrases.objects.filter(topic=SCRIPT_ENDER)


class ScriptCustomProcessor(DefaultProcessor):

    def __init__(self, phrases_pks):
        super().__init__()
        self.phrases_pks=phrases_pks

    def gain_phrases(self):
        return Phrases.objects.filter(pk__in=self.phrases_pks)
