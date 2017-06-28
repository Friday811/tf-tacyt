#!/usr/bin/env python

from tft import TFTacyt
from tftutils import TFTUtils
import pickle
import random
import numpy as np
import tflearn

APPDATAFILE = 'appdata'

api = TFTUtils.readAPI('keys.api')
categories = TFTUtils.getCategoriesFromFile(APPDATAFILE)
TFT = TFTacyt(api, categories, verbosity=TFTUtils.SILENT)

api = TFT.api
categories = TFT.categories
RESET = False
TRAIN = False
if RESET:
    # Get results for malicious apps and read them into data and labels
    with open("maliciousapps/XavierApps.txt") as f:
        content = f.readlines()
    with open("maliciousapps/JudyApps.txt") as f:
        content.extend(f.readlines())
    content = [x.rstrip('\r\n') for x in content]
    data, labels = TFT.createDLPairFromList(content, malicious=True)
    # Get known good apps and read them in to the corpus
    goodTerms = ["developerName:\"Google Inc.\"",
                 "developerName:\"Gameloft\"",
                 "developerName:\"Facebook\""]
    sData, sLabel = TFT.createDLPairFromList(goodTerms, malicious=False)
    data.extend(sData)
    labels = np.append(labels, sLabel, axis=0)
    # Pickle it to use later because searching takes forever.
    pickle.dump(data, open("pickles/corpus_data_XJ.pickle", "wb"))
    pickle.dump(labels, open("pickles/corpus_labels_XJ.pickle", "wb"))
else:
    data = pickle.load(open("pickles/corpus_data_XJ.pickle", "rb"))
    labels = pickle.load(open("pickles/corpus_labels_XJ.pickle", "rb"))
# Randomize the order, important for training
data, labels = TFT.randomizeData(data, labels)
# Normalize the data by category, since not one category should weigh
# more than any other category, normalizing is important.
data = TFT.normalizeDataByCategory(data)
# Remove random testing set
testSet = []
testSetLabels = []
for i in range(100):
    j = random.randrange(0, len(data), 1)
    testSet.append(data.pop(j))
    testSetLabels.append(labels[j])
    labels = np.delete(labels, j, axis=0)
# Print for debug.
TFT.vPrint(data)
TFT.vPrint(type(data))
for i in data:
    TFT.vPrint(str(len(i)) + ' : ' + str(i))
TFT.vPrint(labels)
TFT.vPrint(type(labels))
TFT.vPrint(labels.shape)
TFT.vPrint(labels.dtype)
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
    # model.load("models/XJ_GGF_model.tflearn")
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
        TFT.vPrint("Test set #" + str(i+1) +
               " correctly identified malicious.")
        cM = cM + 1
    elif (pred[i][0] > pred[i][1]) and (testSetLabels[i][0] < testSetLabels[i][1]):
        TFT.vPrint("Test set #" + str(i+1) +
               " false positively identified malicious.")
        fP = fP + 1
    elif (pred[i][0] < pred[i][1]) and (testSetLabels[i][0] < testSetLabels[i][1]):
        TFT.vPrint("Test set #" + str(i+1) + " correctly identified safe.")
        cS = cS + 1
    elif (pred[i][0] < pred[i][1]) and (testSetLabels[i][0] > testSetLabels[i][1]):
        TFT.vPrint("Test set #" + str(i+1) + " incorrectly marked safe.")
        iS = iS + 1
    i = i + 1
print("Correctly identified malicious: " + str(cM) + "/" + str(cM + iS))
print("False positives: " + str(fP) + "/" + str(fP+cS))

