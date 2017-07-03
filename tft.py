# TensorFlow-Tacyt
#
# This script connects to 11Path's Tacyt database
# and learns to identify malicious applications.
# Connection to Tacyt through the tacyt python API.
# Machine learning through TFLearn and TensorFlow.
#
# Copyright (C) 2017 Rafael Ortiz <rafael@ortizmail.cc>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
# USA

from __future__ import print_function
from __future__ import division
import os
from tacyt import TacytApp as ta
import json
import tflearn
import numpy as np
import random
import hashlib
import pickle
from tftutils import TFTUtils
from tftsa import SentimentAnalyzer as SA


class TFTacyt(object):
    """
    TensorFlow-Tacyt Class
    See example.py for usage information.
    """

    def __init__(self, api, categories, verbosity=0):
        # Instantiate
        self.api = api
        self.categories = categories
        self.verbosity = verbosity
        self.DATA = []
        self.LABELS = -1
        self.MODEL = None
        self.Util = TFTUtils(self.verbosity)
        self.vPrint(('Categories: ' + str(self.categories)), self.Util.DEBUG)
        self.SA = SA(verbosity=self.verbosity)
        self.STRDATA = []

    # Use as shorthand for printing informational/debug
    # stuff, will only print when VERBOSE = True
    def vPrint(self, message, verbosity=TFTUtils.DEBUG):
        self.Util.vPrint(message, verbosity)

    # Get the categories to learn from the given file and return it.
    # This allows you to easily select which criteria will be used
    # to learn and search.
    #
    # File should be formatted with one category per line. Lines
    # commented with # will be ignored
    @staticmethod
    def getCategoriesFromFile(fileName):
        categories = []
        with open(fileName) as f:
            lines = f.readlines()
        for line in lines:
            if line[0] != '#':
                categories.append(line.rstrip(os.linesep))
        return categories

    # Given a results json from tacyt and a list of categories to
    # learn from, return a list of dictionaries for each app with
    # any key not in the list of categories removed.
    # If categories are not specified, return all.
    # If a category is not found, it will be instantiated with the notFound var.
    # If notFound is None, no replacement will be made
    @staticmethod
    def getFormattedApplicationsFromResults(results, categories=[], notFound=None):
        apps = []
        categoriesLen = len(categories)
        for app in results['result']['applications']:
            if categoriesLen:
                for key in app.keys():
                    # Remove any keys not in categories
                    if key not in categories:
                        app.pop(key, None)
                apps.append(app)
            else:
                apps.append(app)
        if notFound is not None:
            for app in apps:
                appKeys = app.keys()
                for cat in categories:
                    if cat not in appKeys:
                        app[cat] = notFound
        return apps

    # Takes the strings in app descriptions and hashes them to unique
    # integer values. Should be normalized after. Usefullness will
    # depend on the model you use.
    @staticmethod
    def hashAppStrings(apps):
        for app in apps:
            for key in app.keys():
                if not (type(app[key]) == int or type(app[key]) == float):
                    app[key] = int(
                        hashlib.md5(app[key].encode('utf-8')).hexdigest(),
                        16)
        return apps

    # Given a list of dictionaries corresponding to apps,
    # remove all elements from those dictionaries that are not ints
    # or set them to a specific int
    @staticmethod
    def getIntFilteredAppDict(apps, setTo=None):
        if setTo is None:
            for app in apps:
                for key in app.keys():
                    if not (type(app[key]) == int or type(app[key]) == float):
                        app.pop(key, None)
        else:
            for app in apps:
                for key in app.keys():
                    if not (type(app[key]) == int or type(app[key]) == float):
                        app[key] = setTo
        return apps

    # Strips strings out of the app dict, adding them to STRDATA
    # and adding them to the LSTM model.
    def stripStrings(self, apps, malicious=False):
        for app in apps:
            appStrings = []
            for key in app.keys():
                if type(app[key]) is unicode:
                    app[key] = app[key].encode('utf-8')
                    self.Util.vPrint("Decoded: " + app[key], self.Util.DEBUG)
                    self.Util.vPrint("Type: " + str(type(app[key])), self.Util.DEBUG)
                self.Util.vPrint(app[key], self.Util.DEBUG)
                self.Util.vPrint("Type: " + str(type(app[key])), self.Util.DEBUG)
                if type(app[key]) is str:
                    appStrings.append(app[key])
                    app[key] = -1
                elif type(app[key]) is list:
                    for el in app[key]:
                        if type(el) is unicode:
                            el = el.encode('utf-8')
                        if type(el) is str:
                            appStrings.append(el)
                            self.Util.vPrint(el, self.Util.DEBUG)
                    app[key] = -1
                elif not (type(app[key]) is int or type(app[key]) is float):
                    app[key] = -1
            self.SA.addToCorpus(appStrings, malicious=malicious)
            self.STRDATA.append(appStrings)
            self.Util.vPrint(appStrings, self.Util.DEBUG)
        return apps

    # Create a training data set from a list of app dicts
    # Returns data, a list of lists sorted the same for each app
    # and the labels for the categories [malicious, benign]
    @staticmethod
    def createTrainingSet(apps, malicious=False):
        data = []
        if malicious:
            labels = np.repeat(np.array([[1., 0.]]), [len(apps)], axis=0)
        else:
            labels = np.repeat(np.array([[0., 1.]]), [len(apps)], axis=0)
        for app in apps:
            appList = []
            for key in sorted(app):
                appList.append(app[key])
            data.append(appList)
        return data, labels

    # Set all values for app features to be the same for the entire
    # list of dicts given. Used for debugging that the damn thing works.
    @staticmethod
    def setAllValues(apps, value=True):
        for app in apps:
            for key in app:
                app[key] = value
        return apps

    # Normalize the relative values for each app to each other
    # only works if all values are int or float
    @staticmethod
    def normalizeByApp(apps, nValue=1.0):
        for app in apps:
            maxValue = max(app)
            maxValue = app[maxValue]
            if maxValue == 0:
                maxValue = 1
            for key in app:
                app[key] = (app[key] / float(maxValue)) * nValue
        return apps

    # Normalize the relative values for each app to every other app
    # for that category. Only works if all values are int or float.
    @staticmethod
    def normalizeByCategory(apps, nValue=1.0):
        maxValue = -1
        for key in apps[0].keys():
            # Find max
            for app in apps:
                if app[key] > maxValue:
                    maxValue = app[key]
            # Normalize
            # If the maxValue is -1, then all values for this key are
            # -1, which means no app has it, or it is a string/list
            # and can be removed
            if maxValue == -1:
                for app in apps:
                    app.pop(key, None)
            # If the max value is zero, set to 1 so we can normalize
            # without damaging the universe
            elif maxValue == 0:
                maxValue = 1
            for app in apps:
                app[key] = (app[key] / float(maxValue)) * nValue
            # Reset max value
            maxValue = 0
        return apps

    # Same as the normalizeByCategory function, except for operating
    # on the data list of lists, instead of the apps list of dicts
    def normalizeDataByCategory(self, data, nValue=100.0):
        maxValue = 0
        for i in range(len(data[0])):
            for app in data:
                if app[i] > maxValue:
                    maxValue = app[i]
                    self.vPrint("Staged max: " + str(maxValue), self.Util.DEBUG)
            # Normalize
            self.vPrint("Max value: " + str(maxValue), self.Util.DEBUG)
            if maxValue == 0:
                maxValue = 1
            for app in data:
                app[i] = (app[i] / float(maxValue)) * nValue
                self.vPrint("New normal: " + str(app[i]), self.Util.DEBUG)
            maxValue = 0
        return data

    # Search for 1000 entries for the given string and format it with
    # the given categories argument
    def maxSearch(self, searchString=''):
        api = self.api
        categories = self.categories
        results = []
        for i in range(10):
            try:
                self.vPrint("Searching for " + searchString + " page " + str(i+1), self.Util.DEBUG)
                search = api.search_apps(searchString, maxResults=100, numberPage=i+1)
                search = self.getFormattedApplicationsFromResults(
                    search.get_data(),
                    categories=categories,
                    notFound=-1)
                results.extend(search)
            except AttributeError as e:
                self.vPrint("Encountered an error while searching: " + str(e), self.Util.ERROR)
        return results

    # Randomize data and labels.
    @staticmethod
    def randomizeData(data, labels):
        a = []
        b = []
        combined = list(zip(data, labels))
        random.shuffle(combined)
        a[:], b[:] = zip(*combined)
        b = np.array(b)
        return a, b

    # Creates a data, labels pair from the given API and list of search terms
    # The categories should be passed as well.
    def createDLPairFromList(self, searchTerms, malicious=False):
        api = self.api
        categories = self.categories
        data = []
        labels = -1
        for term in searchTerms:
            search = self.maxSearch(searchString=term)
            search = self.stripStrings(search, malicious=malicious)
            sData, sLabel = TFTacyt.createTrainingSet(search, malicious=malicious)
            data.extend(sData)
            if type(labels) is int:
                labels = sLabel
            else:
                labels = np.append(labels, sLabel, axis=0)
        return data, labels

    #########################################################################
    # Helper methods: These methods call other methods from the class to    #
    #                 make it easier to load data, search, save, etc.       #
    #                                                                       #
    # You should be able to, with these methods:                            #
    #       Create a dataset from a list of search words:                   #
    #           addDatasetFromTerms(searchTerms)                            #
    #       Save and load the dataset: saveDataset(), loadDataset()         #
    #       Preprocess it for learning: preprocess()                        #
    #       Remove a set of validation data: createTestingSet()             #
    #       Create, save, and load a model.                                 #
    #       Validate the model from testing set.                            #
    #                                                                       #
    # It should be possible to recreate their functionality with the        #
    # functions they wrap, if you want to modify parts in the middle.       #
    #########################################################################

    # Wrapper function for createDLPairFromList that stores data and label as
    # variables local to the TFT instance
    def addDatasetFromTerms(self, searchTerms, malicious=False):
        data, labels = self.createDLPairFromList(searchTerms, malicious=malicious)
        self.DATA.extend(data)
        if type(self.LABELS) is int:
            self.LABELS = labels
        else:
            self.LABELS = np.append(self.LABELS, labels, axis=0)
        return self.DATA, self.LABELS

    # Save the data, labels to file
    def saveDataset(self, filename="pickles/dataset.pickle"):
        combined = list(zip(self.DATA, self.LABELS))
        pickle.dump(combined, open(filename, "wb"))
        self.SA.saveDataset()

    # Load the data, labels from file
    def loadDataset(self, filename="pickles/dataset.pickle"):
        combined = pickle.load(open(filename, "rb"))
        a = []
        b = []
        a[:], b[:] = zip(*combined)
        b = np.array(b)
        self.DATA = a
        self.LABELS = b
        self.SA.loadDataset()
        return a, b

    # Preprocesses data by randomizing the order and normalizing by category
    def preprocess(self):
        self.DATA, self.LABELS = self.randomizeData(self.DATA, self.LABELS)
        self.DATA = self.normalizeDataByCategory(self.DATA)

    # Creates a test set of data, removed from training set
    # for validation of the model.
    def createTestingSet(self, size=-1):
        if size == -1:
            size = len(self.DATA) // 10
        testSet = []
        testSetLabels = []
        for i in range(size):
            j = random.randrange(0, len(self.DATA), 1)
            testSet.append(self.DATA.pop(j))
            testSetLabels.append(self.LABELS[j])
            self.LABELS = np.delete(self.LABELS, j, axis=0)
        return testSet, testSetLabels

    # Data must exist before the model is created
    def createModel(self):
        self.SA.createCorpusID()
        net = tflearn.input_data(shape=[None, len(self.DATA[0])])
        net = tflearn.fully_connected(net, 32)
        net = tflearn.fully_connected(net, 32)
        net = tflearn.fully_connected(net, 2, activation='softmax')
        adam = tflearn.optimizers.Adam(learning_rate=0.0001)
        net = tflearn.regression(net, optimizer=adam)
        model = tflearn.DNN(net, tensorboard_verbose=self.verbosity)
        self.MODEL = model

    def trainModel(self):
        self.SA.preprocessData()
        self.SA.createModel()
        self.SA.trainModel()
        self.MODEL.fit(self.DATA,
                       self.LABELS,
                       n_epoch=1000,
                       batch_size=32,
                       show_metric=True
                       )

    def saveModel(self, filename='models/model.tflearn'):
        if self.MODEL is None:
            self.createModel()
        self.MODEL.save(filename)
        self.SA.saveModel()

    def loadModel(self, filename='models/model.tflearn'):
        if self.MODEL is None:
            self.createModel()
        self.MODEL.load(filename)
        self.SA.loadModel()

    def validateModel(self, testSet, testSetLabels):
        pred = self.MODEL.predict(testSet)
        fP = 0
        cM = 0
        cS = 0
        iS = 0
        i = 0
        for el in pred:
            if (pred[i][0] > pred[i][1]) and (testSetLabels[i][0] > testSetLabels[i][1]):
                self.vPrint("Test set #" + str(i+1) +
                            " correctly identified malicious.",
                            self.Util.DEBUG)
                cM = cM + 1
            elif (pred[i][0] > pred[i][1]) and (testSetLabels[i][0] < testSetLabels[i][1]):
                self.vPrint("Test set #" + str(i+1) +
                            " false positively identified malicious.",
                            self.Util.DEBUG)
                fP = fP + 1
            elif (pred[i][0] < pred[i][1]) and (testSetLabels[i][0] < testSetLabels[i][1]):
                self.vPrint("Test set #" + str(i+1) + " correctly identified safe.",
                            self.Util.DEBUG)
                cS = cS + 1
            elif (pred[i][0] < pred[i][1]) and (testSetLabels[i][0] > testSetLabels[i][1]):
                self.vPrint("Test set #" + str(i+1) + " incorrectly marked safe.",
                            self.Util.DEBUG)
                iS = iS + 1
            i = i + 1
        print("Correctly identified malicious: " + str(cM) + "/" + str(cM + iS))
        print("False positives: " + str(fP) + "/" + str(fP+cS))


if __name__ == '__main__':
    print("ERROR: This module should be imported, not run.\
         \n       See example.py for usage.")
