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


class TFTacyt(object):
    """
    TensorFlow-Tacyt Class
    """

    def __init__(self, api, categories, verbosity=0):
        self.api = api
        self.categories = categories
        self.verbosity = verbosity
        self.Util = TFTUtils(self.verbosity)
        self.vPrint(('Categories: ' + str(self.categories)), self.Util.DEBUG)

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
        maxValue = 0
        for key in apps[0].keys():
            # Find max
            for app in apps:
                if app[key] > maxValue:
                    maxValue = app[key]
            # Normalize
            if maxValue == 0:
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
            self.vPrint("Searching for " + searchString + " page " + str(i+1), self.Util.DEBUG)
            search = api.search_apps(searchString, maxResults=100, numberPage=i+1)
            search = self.getFormattedApplicationsFromResults(
                search.get_data(),
                categories=categories,
                notFound=-1)
            results.extend(search)
        return results

    # Randomize data and labels, very important for training if you
    # build your data sets per category.
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
            search = TFTacyt.getIntFilteredAppDict(search, setTo=-1)
            sData, sLabel = TFTacyt.createTrainingSet(search, malicious=malicious)
            data.extend(sData)
            if type(labels) is int:
                labels = sLabel
            else:
                labels = np.append(labels, sLabel, axis=0)
        return data, labels


if __name__ == '__main__':
    print("ERROR: This module should be imported, not run.\
         \n       See example.py for usage.")
