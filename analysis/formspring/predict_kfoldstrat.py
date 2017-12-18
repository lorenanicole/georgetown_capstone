#!/usr/bin/python

import pickle
import numpy
numpy.random.seed(42)
import pprint
# metric model to evaluate the model performance
from sklearn import metrics
from sklearn.model_selection import StratifiedShuffleSplit

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
    pass
    #print(type(comment), type(label))
    #if comment == None:
    #print(comment, label)
    #print(count)

#print(count)
### test_size is the percentage of events assigned to the test set (the
### remainder go into training)
### feature matrices changed to dense representations for compatibility with
### classifier functions in versions 0.15.2 and earlier
from sklearn import model_selection
#features_train, features_test, labels_train, labels_test = model_selection.train_test_split(word_data,
#                                                            labels_data, test_size=0.2, random_state=42)

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

vectorizer = TfidfVectorizer(sublinear_tf=True, max_df=0.20, ngram_range = (1,2),
                             max_features = 100000, stop_words='english')

#pprint.pprint(vectorizer.transform(features_train))

#features_train = vectorizer.fit_transform(features_train)
#features_test  = vectorizer.transform(features_test)
#pprint.pprint(vectorizer.get_feature_names())

from sklearn import tree
from sklearn.metrics import accuracy_score

clf = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(15,4), random_state=1)
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

# testing accuracy
#print(metrics.accuracy_score(labels_test, pred))
#print(metrics.classification_report(labels_test, pred))

#Kfold stratified cross validation
sss = StratifiedShuffleSplit(n_splits=10, test_size = 0.1, random_state = 42)
#print (sss)
true_negatives = 0
false_negatives = 0
true_positives = 0
false_positives = 0

for train_idx, test_idx in sss.split(word_data, labels_data):
    #print(len(train_idx), len(test_idx))
    #sum_labels_train = 0
    #sum_labels_test =0
    features_train = []
    features_test  = []
    labels_train   = []
    labels_test    = []
    for ii in train_idx:
        features_train.append( word_data[ii] )
        labels_train.append( labels_data[ii] )
        #sum_labels_train += labels_data[ii]
    for jj in test_idx:
        features_test.append( word_data[jj] )
        labels_test.append( labels_data[jj] )
        #sum_labels_test += labels_data[jj]
    #print(sum_labels_train, sum_labels_test)
    vectorizer = TfidfVectorizer(sublinear_tf=True, max_df=0.20, ngram_range = (1,2),
                                 max_features = 100000, stop_words='english')
    features_train = vectorizer.fit_transform(features_train)
    features_test  = vectorizer.transform(features_test)
    clf = clf.fit(features_train, labels_train)
    predictions = clf.predict(features_test)
    for prediction, truth in zip(predictions, labels_test):
        if prediction == 0 and truth == 0:
            true_negatives += 1
        elif prediction == 0 and truth == 1:
            false_negatives += 1
        elif prediction == 1 and truth == 0:
            false_positives += 1
        elif prediction == 1 and truth == 1:
            true_positives += 1
        else:
            print(type(prediction), prediction)
            print ("Warning: Found a predicted label not == 0 or 1.")
            print ("All predictions should take value 0 or 1.")
            print ("Evaluating performance for processed predictions:")
            break
try:
    total_predictions = true_negatives + false_negatives + false_positives + true_positives
    accuracy = 1.0*(true_positives + true_negatives)/total_predictions
    precision = 1.0*true_positives/(true_positives+false_positives)
    recall = 1.0*true_positives/(true_positives+false_negatives)
    f1 = 2.0 * true_positives/(2*true_positives + false_positives+false_negatives)
    f2 = (1+2.0*2.0) * precision*recall/(4*precision + recall)
    print (clf)
    print (PERF_FORMAT_STRING.format(accuracy, precision, recall, f1, f2, display_precision = 5))
    print (RESULTS_FORMAT_STRING.format(total_predictions, true_positives, false_positives, false_negatives, true_negatives))
    print ("")
except:
    print ("Got a divide by zero when trying out:", clf)
    print ("Precision or recall may be undefined due to a lack of true positive predicitons.")
