#!/usr/bin/env python

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

VERBOSE = True
APPDATAFILE = 'appdata'


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


def hashAppStrings(apps):
    for app in apps:
        for key in app.keys():
            if not (type(app[key]) == int or type(app[key]) == float):
                app[key] = int(hashlib.md5(app[key].encode('utf-8')).hexdigest(), 16)
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
        if maxValue == 0: maxValue = 1
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
        if maxValue == 0: maxValue = 1
        for app in apps:
            app[key] = (app[key] / float(maxValue)) * nValue
        # Reset max value
        maxValue = 0
    return apps


def normalizeDataByCategory(data, nValue=100.0):
    maxValue = 0
    for i in range(len(data[0])):
        for app in data:
            if app[i] > maxValue:
                maxValue = app[i]
                if VERBOSE: print("Staged max: " + str(maxValue))
        # Normalize
        if VERBOSE: print("Max value: " + str(maxValue))
        if maxValue == 0: maxValue = 1
        for app in data:
            app[i] = (app[i] / float(maxValue)) * nValue
            if VERBOSE:
                print("New normal: " + str(app[i]))
        maxValue = 0
    return data


# Search for 1000 entries for the given string and format it with
# the given categories argument
def maxSearch(api, searchString='', categories=[]):
    results = []
    for i in range(10):
        if VERBOSE:
            print("Searching for " + searchString + " page " + str(i+1))
        search = api.search_apps(searchString, maxResults=100, numberPage=i+1)
        search = getFormattedApplicationsFromResults(search.get_data(), categories=categories, notFound=-1)
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
    test_search = maxSearch(api, searchString="developerName:\"Google Inc.\"", categories=categories)
    test_search_mal = maxSearch(api, searchString="developerName:\"Gameloft\"", categories=categories)
    formattedResults = getIntFilteredAppDict(test_search, setTo=-1)
    formattedResultsMal = getIntFilteredAppDict(test_search_mal, setTo=-1)
    formattedResults = normalizeByCategory(formattedResults)
    formattedResultsMal = normalizeByCategory(formattedResultsMal)
    # print(json.dumps(formattedResults, indent=2))
    data, labels = createTrainingSet(formattedResults, malicious=False)
    data_mal, labels_mal = createTrainingSet(formattedResultsMal, malicious=True)
    labels = np.append(labels, labels_mal, axis=0)
    data.extend(data_mal)
    pickle.dump(data, open("data.pickle", "wb"))
    pickle.dump(labels, open("labels.pickle", "wb"))
    #data = pickle.load(open("data.pickle", "rb"))
    #labels = pickle.load(open("labels.pickle", "rb"))
    data, labels = randomizeData(data, labels)
    data = normalizeDataByCategory(data)
    print(data)
    print(type(data))
    for i in data:
        print(str(len(i)) + ' : ' + str(i))
    print(labels)
    print(type(labels))
    print(labels.shape)
    print(labels.dtype)
    # Build neural network
    net = tflearn.input_data(shape=[None, len(data[0])])
    net = tflearn.fully_connected(net, 32)
    net = tflearn.fully_connected(net, 32)
    net = tflearn.fully_connected(net, 2, activation='softmax')
    adam = tflearn.optimizers.Adam(learning_rate=0.01)
    net = tflearn.regression(net, optimizer=adam)
    # Define model.
    model = tflearn.DNN(net, tensorboard_verbose=3)
    # Start training.
    model.fit(data, labels, n_epoch=100, batch_size=32, show_metric=True)
    rand = []
    r_label = []
    for i in range(10):
        j = random.randrange(0, len(data), 1)
        rand.append(data[j])
        r_label.append(labels[j])

    pred = model.predict(rand)
    i = 0
    for el in pred:
        print(rand[i])
        print(r_label[i])
        print("Random (Gameloft) pred: ", pred[i][0])
        print("Random (Google) pred: ", pred[i][1])
        i = i + 1


def main():
    if VERBOSE:
        print("Verbose mode.")
    keys = open('keys.api')
    API_ID = keys.readline().rstrip(os.linesep)[7:]
    SECRET = keys.readline().rstrip(os.linesep)[7:]
    keys.close()
    categories = getCategoriesFromFile(APPDATAFILE)
    if VERBOSE:
        print("API_ID: " + API_ID)
        print("SECRET: " + SECRET)
        print("Categories: ")
        print(categories)
    api = ta.TacytApp(API_ID, SECRET)
    testSearch(api, categories)


if __name__ == '__main__':
    main()
