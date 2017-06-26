#!/usr/bin/env python

from __future__ import print_function
import os
from tacyt import TacytApp as ta

VERBOSE = True


def testSearch(api):
    test_search = api.search_apps("title:\"5G Speed For Android\"")
    print(test_search.get_data())
    print(test_search.get_error())


def main():
    if VERBOSE:
        print("Verbose mode.")
    keys = open('keys.api')
    API_ID = keys.readline().rstrip(os.linesep)[7:]
    SECRET = keys.readline().rstrip(os.linesep)[7:]
    if VERBOSE:
        print("API_ID: " + API_ID)
        print("SECRET: " + SECRET)
    api = ta.TacytApp(API_ID, SECRET)
    testSearch(api)


if __name__ == '__main__':
    main()
