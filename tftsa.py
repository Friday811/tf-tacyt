from __future__ import division, print_function, absolute_import

import tflearn
from tflearn.data_utils import to_categorical, pad_sequences
import numpy as np
import re
from tftutils import TFTUtils
import pickle
import tensorflow as tf


class SentimentAnalyzer(object):
    """
    Implement sentiment analysis in tflearn to learn
    malicious vs nonmalicious sentiment from a 'sentence.'
    """

    def __init__(self, verbosity=0):
        self.corpus = []
        self.corpusID = {}
        self.data = []
        self.labels = []
        self.verbosity = verbosity
        self.Util = TFTUtils(self.verbosity)
        self.model = None

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
                    entryL.extend(self.parseSentence(i))
            elif type(entry) is str:
                entryL.extend(self.parseSentence(entry))
            self.data[self.data.index(entry)] = entryL
            self.Util.vPrint(entryL, self.Util.DEBUG)
        maxlen = len(max(self.data, key=len))
        self.data = pad_sequences(self.data, maxlen=maxlen, value=0.)
        self.Util.vPrint(self.data, self.Util.DEBUG)
        self.labels = np.array(self.labels)
        self.Util.vPrint(self.labels, self.Util.DEBUG)

    def createModel(self):
        self.Util.vPrint("Creating SA Model.", self.Util.DEBUG)
        net = tflearn.input_data([None, len(self.data[0])])
        net = tflearn.embedding(net,
                                input_dim=len(self.corpusID) + 1,
                                output_dim=128)
        self.Util.vPrint("Corpus ID Length: " +
                         str(len(self.corpusID)),
                         self.Util.DEBUG)
        net = tflearn.lstm(net, 128, dropout=0.8, dynamic=True)
        net = tflearn.fully_connected(net, 2, activation='softmax')
        net = tflearn.regression(net, optimizer='adam', learning_rate=0.001,
                                 loss='categorical_crossentropy')
        model = tflearn.DNN(net, tensorboard_verbose=0)
        self.model = model

    def trainModel(self):
        tf.reset_default_graph()
        if self.model is None:
            self.createModel()
        self.Util.vPrint("Data: ", self.Util.DEBUG)
        self.Util.vPrint(str(self.data), self.Util.DEBUG)
        self.Util.vPrint("Len: " + str(len(self.data)) +
                         " len([0]): " + str(len(self.data[0])),
                         self.Util.DEBUG)
        self.Util.vPrint("Labels: ", self.Util.DEBUG)
        self.Util.vPrint(str(self.labels), self.Util.DEBUG)
        self.Util.vPrint(self.labels.shape, self.Util.DEBUG)
        self.model.fit(self.data,
                       self.labels,
                       show_metric=True,
                       batch_size=None)

    def saveModel(self, filename='models/lstmmodel.tflearn'):
        if self.model is None:
            self.createModel()
        else:
            self.model.save(filename)

    def loadModel(self, filename='models/lstmmodel.tflearn'):
        if self.model is None:
            self.createModel()
        self.model.load(filename)

    def saveDataset(self, filename='pickles/datasetsa.pickle'):
        self.createCorpusID()
        combined = list(zip(self.data, self.labels))
        pickle.dump(combined, open(filename, "wb"))
        pickle.dump(self.corpusID, open('pickles/datasetCID.pickle', "wb"))

    def loadDataset(self, filename='pickles/datasetsa.pickle'):
        combined = pickle.load(open(filename, "rb"))
        a = []
        b = []
        a[:], b[:] = zip(*combined)
        b = np.array(b)
        self.data = a
        self.labels = b
        self.corpusID = pickle.load(open('pickles/datasetCID.pickle', "rb"))
        self.Util.vPrint("CorpusID loaded: " +
                         str(self.corpusID),
                         self.Util.DEBUG)
        return a, b


def main():
    SA = SentimentAnalyzer(TFTUtils.DEBUG)
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
    SA.createModel()
    SA.trainModel()


if __name__ == '__main__':
    main()
