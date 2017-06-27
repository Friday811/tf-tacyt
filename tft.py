#!/usr/bin/env python
# TensorFlow-Tacyt

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

VERBOSE = False
APPDATAFILE = 'appdata'


# Use as shorthand for printing informational/debug
# stuff, will only print when VERBOSE = True
def vPrint(message):
    if VERBOSE:
        print(message)


# Get the categories to learn from the given file and return it.
# This allows you to easily select which criteria will be used
# to learn and search.
#
# File should be formatted with one category per line. Lines
# commented with # will be ignored
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
def setAllValues(apps, value=True):
    for app in apps:
        for key in app:
            app[key] = value
    return apps


# Normalize the relative values for each app to each other
# only works if all values are int or float
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
def normalizeDataByCategory(data, nValue=100.0):
    maxValue = 0
    for i in range(len(data[0])):
        for app in data:
            if app[i] > maxValue:
                maxValue = app[i]
                vPrint("Staged max: " + str(maxValue))
        # Normalize
        vPrint("Max value: " + str(maxValue))
        if maxValue == 0:
            maxValue = 1
        for app in data:
            app[i] = (app[i] / float(maxValue)) * nValue
            vPrint("New normal: " + str(app[i]))
        maxValue = 0
    return data


# Search for 1000 entries for the given string and format it with
# the given categories argument
def maxSearch(api, searchString='', categories=[]):
    results = []
    for i in range(10):
        vPrint("Searching for " + searchString + " page " + str(i+1))
        search = api.search_apps(searchString, maxResults=100, numberPage=i+1)
        search = getFormattedApplicationsFromResults(
            search.get_data(),
            categories=categories,
            notFound=-1)
        results.extend(search)
    return results


# Randomize data and labels, very important for training if you
# build your data sets per category.
def randomizeData(data, labels):
    a = []
    b = []
    combined = list(zip(data, labels))
    random.shuffle(combined)
    a[:], b[:] = zip(*combined)
    b = np.array(b)
    return a, b


# This function is a scratchpad and a total mess.
def testSearch(api, categories):
    RESET = False
    TRAIN = False
    if RESET:
        # Create the list to hold data and NumPy array to hold labels
        data = []
        labels = -1  # instantiate on first use //yesitsahack
        # Get results for malicious apps and read them into data and labels
        with open("maliciousapps/XavierApps.txt") as f:
            content = f.readlines()
        content = [x.rstrip('\r\n') for x in content]
        for pName in content:
            search = maxSearch(api, searchString=("packageName:" + pName),
                               categories=categories)
            search = getIntFilteredAppDict(search, setTo=-1)
            sData, sLabel = createTrainingSet(search, malicious=True)
            data.extend(sData)
            vPrint(str(labels))
            vPrint(str(sLabel))
            if type(labels) is int:
                labels = sLabel
            else:
                labels = np.append(labels, sLabel, axis=0)
        with open("maliciousapps/JudyApps.txt") as f:
            content = f.readlines()
        content = [x.rstrip('\r\n') for x in content]
        for pName in content:
            search = maxSearch(api, searchString=("packageName:" + pName),
                               categories=categories)
            search = getIntFilteredAppDict(search, setTo=-1)
            sData, sLabel = createTrainingSet(search, malicious=True)
            data.extend(sData)
            labels = np.append(labels, sLabel, axis=0)
        # Get known good apps and read them in to the corpus
        search = maxSearch(api, searchString="developerName:\"Google Inc.\"",
                           categories=categories)
        search = getIntFilteredAppDict(search, setTo=-1)
        sData, sLabel = createTrainingSet(search, malicious=False)
        data.extend(sData)
        labels = np.append(labels, sLabel, axis=0)
        search = maxSearch(api, searchString="developerName:\"Gameloft\"",
                           categories=categories)
        search = getIntFilteredAppDict(search, setTo=-1)
        sData, sLabel = createTrainingSet(search, malicious=False)
        data.extend(sData)
        labels = np.append(labels, sLabel, axis=0)
        search = maxSearch(api, searchString="developerName:\"Facebook\"",
                           categories=categories)
        search = getIntFilteredAppDict(search, setTo=-1)
        sData, sLabel = createTrainingSet(search, malicious=False)
        data.extend(sData)
        labels = np.append(labels, sLabel, axis=0)
        # Pickle it to use later because searching takes forever.
        pickle.dump(data, open("pickles/corpus_data_XJ.pickle", "wb"))
        pickle.dump(labels, open("pickles/corpus_labels_XJ.pickle", "wb"))
    else:
        data = pickle.load(open("pickles/corpus_data_XJ.pickle", "rb"))
        labels = pickle.load(open("pickles/corpus_labels_XJ.pickle", "rb"))
    # Randomize the order, important for training
    data, labels = randomizeData(data, labels)
    # Normalize the data by category, since not one category should weigh
    # more than any other category, normalizing is important.
    data = normalizeDataByCategory(data)
    # Remove random testing set
    testSet = []
    testSetLabels = []
    for i in range(100):
        j = random.randrange(0, len(data), 1)
        testSet.append(data.pop(j))
        testSetLabels.append(labels[j])
        labels = np.delete(labels, j, axis=0)
    # Print for debug.
    vPrint(data)
    vPrint(type(data))
    for i in data:
        vPrint(str(len(i)) + ' : ' + str(i))
    vPrint(labels)
    vPrint(type(labels))
    vPrint(labels.shape)
    vPrint(labels.dtype)
    # Build neural network
    net = tflearn.input_data(shape=[None, len(data[0])])
    net = tflearn.fully_connected(net, 32)
    net = tflearn.fully_connected(net, 32)
    net = tflearn.fully_connected(net, 2, activation='softmax')
    adam = tflearn.optimizers.Adam(learning_rate=0.0001)
    net = tflearn.regression(net, optimizer=adam)
    # Define model.
    model = tflearn.DNN(net, tensorboard_verbose=3)
    if TRAIN:
        model.load("models/XJ_GGF_model.tflearn")
        # Start training.
        model.fit(data, labels, n_epoch=1000, batch_size=32, show_metric=True)
        # Save the model
        model.save("models/XJ_GGF_model.tflearn")
    else:
        model.load("models/XJ_GGF_model.tflearn")
    # Test the models predictions
    pred = model.predict(testSet)
    fP = 0
    cM = 0
    cS = 0
    iS = 0
    i = 0
    for el in pred:
        if (pred[i][0] > pred[i][1]) and (testSetLabels[i][0] > testSetLabels[i][1]):
            vPrint("Test set #" + str(i+1) + " correctly identified malicious.")
            cM = cM + 1
        elif (pred[i][0] > pred[i][1]) and (testSetLabels[i][0] < testSetLabels[i][1]):
            vPrint("Test set #" + str(i+1) + " false positively identified malicious.")
            fP = fP + 1
        elif (pred[i][0] < pred[i][1]) and (testSetLabels[i][0] < testSetLabels[i][1]):
            vPrint("Test set #" + str(i+1) + " correctly identified safe.")
            cS = cS + 1
        elif (pred[i][0] < pred[i][1]) and (testSetLabels[i][0] > testSetLabels[i][1]):
            vPrint("Test set #" + str(i+1) + " incorrectly marked safe.")
            iS = iS + 1
        i = i + 1
    print("Correctly identified malicious: " + str(cM) + "/" + str(cM + iS))
    print("False positives: " + str(fP) + "/" + str(fP+cS))


def main():
    vPrint("Verbose mode.")
    keys = open('keys.api')
    API_ID = keys.readline().rstrip(os.linesep)[7:]
    SECRET = keys.readline().rstrip(os.linesep)[7:]
    keys.close()
    categories = getCategoriesFromFile(APPDATAFILE)
    vPrint("API_ID: " + API_ID)
    vPrint("SECRET: " + SECRET)
    vPrint("Categories: ")
    vPrint(categories)
    api = ta.TacytApp(API_ID, SECRET)
    testSearch(api, categories)


if __name__ == '__main__':
    main()
