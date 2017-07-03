#!/usr/bin/env python

from tft import TFTacyt
from tftutils import TFTUtils

APPDATAFILE = 'appdata'

# Create the API, define categories to use, create TFTacyt instance
api = TFTUtils.readAPI('keys.api')
categories = TFTUtils.getCategoriesFromFile(APPDATAFILE)
TFT = TFTacyt(api, categories, verbosity=TFTUtils.DEBUG)

api = TFT.api
categories = TFT.categories
RESET = False
TRAIN = True
if RESET:
    # Get results for malicious apps and add them to the TFT dataset
    with open("maliciousapps/XavierApps.txt") as f:
        content = f.readlines()
    with open("maliciousapps/JudyApps.txt") as f:
        content.extend(f.readlines())
    content = [x.rstrip('\r\n') for x in content]
    TFT.addDatasetFromTerms(content, malicious=True)
    # Get known good apps and add them to the TFT dataset
    goodTerms = ["developerName:\"Google Inc.\"",
                 "developerName:\"Gameloft\"",
                 "developerName:\"Facebook\""]
    TFT.addDatasetFromTerms(goodTerms, malicious=False)
    # Pickle it to use later because searching takes forever.
    TFT.saveDataset()
else:
    TFT.loadDataset()
# Run the sentiment analyzer module on the text data and
# add the predictions to the int/float data
TFT.runSAModel()
# Preprocess data (randomize and normalize)
TFT.preprocess()
# Remove random testing set
# testSet, testSetLabels = TFT.createTestingSet()
# Print for debug.
TFT.vPrint(TFT.DATA)
TFT.vPrint(type(TFT.DATA))
for i in TFT.DATA:
    TFT.vPrint(str(len(i)) + ' : ' + str(i))
TFT.vPrint(TFT.LABELS)
TFT.vPrint(type(TFT.LABELS))
TFT.vPrint(TFT.LABELS.shape)
TFT.vPrint(TFT.LABELS.dtype)
# Build neural network
TFT.createModel()
if TRAIN:
    # Start training.
    TFT.trainModel()
    # Save the model
    TFT.saveModel()
else:
    TFT.loadModel()
# Test the models predictions
# TFT.validateModel(testSet, testSetLabels)
