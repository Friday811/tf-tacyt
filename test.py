#!/usr/bin/env python

from __future__ import print_function
import os
from tacyt import TacytApp as ta
import json

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
def getFormattedApplicationsFromResults(results, categories=[]):
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
    return apps


def testSearch(api, categories):
    test_search = api.search_apps("title:\"5G Speed For Android\"")
    # print(json.dumps(test_search.get_data(), indent=2))
    # print(json.dumps(test_search.get_error(), indent=2))
    print(json.dumps(
        getFormattedApplicationsFromResults(test_search.get_data(),
                                            categories), indent=2))


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
