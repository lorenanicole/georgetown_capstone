#!/usr/bin/python

import pickle
import numpy
numpy.random.seed(42)
from pprint import pprint
from sklearn.pipeline import Pipeline
# metric model to evaluate the model performance
from sklearn import metrics
from sklearn.model_selection import KFold

PERF_FORMAT_STRING = "\
\tAccuracy: {:>0.{display_precision}f}\tPrecision: {:>0.{display_precision}f}\t\
Recall: {:>0.{display_precision}f}\tF1: {:>0.{display_precision}f}\tF2: {:>0.{display_precision}f}"
RESULTS_FORMAT_STRING = "\tTotal predictions: {:4d}\tTrue positives: {:4d}\tFalse positives: {:4d}\
\tFalse negatives: {:4d}\t True negatives: {:4d}"

words_file = "my_dataset.pkl"
labels_file = "my_feature_list.pkl"
word_data = pickle.load( open(words_file, "rb"))
labels_data = pickle.load( open(labels_file, "rb") )

#convert labels_data to integers
labels_data = [int(i) for i in labels_data]


count = 0
#print(word_data[:10])
for comment, label in zip(word_data, labels_data):
    count += 1

### your code goes here
from sklearn.svm import SVC
from sklearn.naive_bayes import  MultinomialNB
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier

vectorizer = TfidfVectorizer(sublinear_tf=True, max_df=0.20, ngram_range = (1,2),
                             max_features = 100000, stop_words='english', use_idf=True)

#pprint.pprint(vectorizer.transform(features_train))

#features_train = vectorizer.fit_transform(features_train)
#features_test  = vectorizer.transform(features_test)
#pprint.pprint(vectorizer.get_feature_names())

from sklearn import tree
from sklearn.metrics import accuracy_score

clf = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(15,4), random_state=1)
pipeline = Pipeline([('tf_idf', vectorizer),
                     ('classifier', clf)
          ])
kf = KFold(n_splits = 12, random_state = 42, shuffle = True)
for train_idx, test_idx in kf.split(word_data, labels_data):
    print(len(train_idx), len(test_idx))
    #print(type(train_idx),type(test_idx))
    #print(train_idx, test_idx)
    #sum_labels_train = 0
    #sum_labels_test =0
    features_train = []
    features_test  = []
    labels_train   = []
    labels_test    = []
    for ii in train_idx:
        features_train.append( word_data[ii] )
        labels_train.append( labels_data[ii] )
        #print(word_data[ii])
        #sum_labels_train += labels_data[ii]
    for jj in test_idx:
        features_test.append( word_data[jj] )
        labels_test.append( labels_data[jj] )
        #sum_labels_test += labels_data[jj]
    #print(sum_labels_train, sum_labels_test)
    pipeline.fit(features_train, labels_train)
    pred = pipeline.predict(features_test)
    print(metrics.accuracy_score(labels_test, pred))
    print(metrics.classification_report(labels_test, pred))
