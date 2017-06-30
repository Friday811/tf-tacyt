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
        self.data = []
        self.labels = []

    # Splits strings on spaces, special chars, etc, from regex
    def splitString(self, string):
        split = []
        for word in re.split('\W+', string):
            split.append(word)
        return split

    # Add the given sentence or list of sentences to the 
    # self.corpus, takes strings or lists containing strings
    def addToCorpus(self, words, malicious=False):
        data = []
        if type(words) is list:
            for sentence in words:
                    self.corpus.extend(self.splitString(sentence))
                    data.append(self.splitString(sentence))
        elif type(words) is str:
            self.corpus.extend(self.splitString(words))
            data.append(self.splitString(words))
        self.data.append(data)
        if malicious:
            self.labels.append([1., 0.])
        else:
            self.labels.append([0., 1.])

    # Uses the existing corpus to assign ID numbers to each
    # string present
    def createCorpusID(self):
        i = 1
        for word in self.corpus:
            if word not in self.corpusID:
                self.corpusID[word] = i
                i = i + 1

    # parses a sentence (either a string or list of strings)
    # into a list of IDs from the corpus ID
    # Any word not found gets the ID of len(corpusID) + 1
    # 0 is reserved for padding
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

    # Preprocess the self.data to prepare it for 
    # use in model training
    def preprocessData(self):
        self.createCorpusID()
        for entry in self.data:
            entryL = []
            if type(entry) is list:
                for i in entry:
                    entryL.extend(parseSentence(i))
            elif type(entry) is str:
                entryL.extend(parseSentence(entry))
            entry = entryL
            

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
    print(SA.labels)
    print(SA.data)
    SA.preprocessData()
    print(SA.data)


if __name__ == '__main__':
    main()
