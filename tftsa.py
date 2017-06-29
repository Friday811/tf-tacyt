from __future__ import division, print_function, absolute_import

import tflearn
from tflearn.data_utils import to_categorical, pad_sequences
import re


class SentimentAnalyzer(object):
    """
    Implement sentiment analysis in tflearn to learn
    malicious vs nonmalicious sentiment from a 'sentence.'
    """

    def __init__(self):
        self.corpus = []
        self.corpusID = {}

    def splitString(self, string):
        split = []
        for word in re.split('\W+', string):
            split.append(word)
        return split

    def addToCorpus(self, words):
        if type(words) is list:
            for sentence in words:
                    self.corpus.extend(self.splitString(sentence))
        elif type(words) is str:
            self.corpus.extend(self.splitString(words))

    def createCorpusID(self):
        i = 1
        for word in self.corpus:
            if word not in self.corpusID:
                self.corpusID[word] = i
                i = i + 1

    def parseSentence(self, sentence):
        words = []
        parsed = []
        if type(sentence) is list:
            for phrase in sentence:
                words.extend(self.splitString(phrase))
        elif type(sentence) is str:
            words.extend(self.splitString(sentence))
        for word in words:
            if word in self.corpusID:
                parsed.append(self.corpusID[word])
            else:
                # 1 past end of corpus is for unknown words
                # 0 will be used for padding
                parsed.append(len(self.corpusID) + 1)
        return parsed


def main():
    SA = SentimentAnalyzer()
    SA.addToCorpus('Hello, world!')
    print(SA.corpus)
    SA.addToCorpus(['Hello again.', 'These are words.'])
    print(SA.corpus)
    SA.addToCorpus('Hey, you - what are you doing here!?')
    SA.createCorpusID()
    print(SA.corpusID)
    print(SA.parseSentence('Hey world, what? unknown'))


if __name__ == '__main__':
    main()
