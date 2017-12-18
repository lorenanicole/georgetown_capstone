#!/usr/bin/python

import pickle
import numpy
import matplotlib.pyplot as plt
numpy.random.seed(42)

PERF_FORMAT_STRING = "\
\tAccuracy: {:>0.{display_precision}f}\tPrecision: {:>0.{display_precision}f}\t\
Recall: {:>0.{display_precision}f}\tF1: {:>0.{display_precision}f}\tF2: {:>0.{display_precision}f}"
RESULTS_FORMAT_STRING = "\tTotal predictions: {:4d}\tTrue positives: {:4d}\tFalse positives: {:4d}\
\tFalse negatives: {:4d}\t True negatives: {:4d}"

words_file = "my_dataset.pkl"
labels_file = "my_feature_list.pkl"
word_data = pickle.load( open(words_file, "rb"))
labels_data = pickle.load( open(labels_file, "rb") )


count = 0
#print(word_data[:10])
for comment, label in zip(word_data, labels_data):
    count += 1
    #if comment == None:
    #print(comment, label)
    #print(count)

#print(count)
### test_size is the percentage of events assigned to the test set (the
### remainder go into training)
### feature matrices changed to dense representations for compatibility with
### classifier functions in versions 0.15.2 and earlier
from sklearn import model_selection
features_train, features_test, labels_train, labels_test = model_selection.train_test_split(word_data, labels_data, test_size=0.1, random_state=42)

"""
features_train = features_train[:2]
labels_train   = labels_train[:2]
features_test = features_test[:2]
labels_test = labels_test[:2]
"""
#print(features_train[:5])
### your code goes here
from sklearn.svm import SVC
from sklearn.naive_bayes import  MultinomialNB
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier

vectorizer = TfidfVectorizer(sublinear_tf=True, max_df=0.5,
                             stop_words='english')

features_train = vectorizer.fit_transform(features_train)
features_test  = vectorizer.transform(features_test)

from yellowbrick.text import TSNEVisualizer
# Create the visualizer and draw the vectors
from sklearn import tree
from sklearn.metrics import accuracy_score

#clf = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(15,4), random_state=1)
#clf = SVC()
#clf = SGDClassifier()
#clf = LogisticRegression()
#clf = tree.DecisionTreeClassifier()
#clf = MultinomialNB()
#clf = clf.fit(features_train, labels_train)
#pred =  clf.predict(features_test)
#accuracy = accuracy_score(pred,labels_test)
#print("accuracy is: ", round(accuracy,3))
#[print(type(int(item))) for item in pred]
