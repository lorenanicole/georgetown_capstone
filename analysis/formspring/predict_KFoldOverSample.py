#!/usr/bin/python

## This file adds an equal population of bully comments to the corpus and carries
## out Text classification using the MLPClassifier. Text features are transformed
## usi TfidfVectorizer and a 12-fold cross validation is applied.

import pickle
import numpy
numpy.random.seed(42)
from pprint import pprint
import pandas as pd
from sklearn.pipeline import Pipeline
# metric model to evaluate the model performance
from sklearn import metrics
from sklearn.model_selection import KFold
from sklearn.svm import SVC
from sklearn.naive_bayes import  MultinomialNB
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
from sklearn import tree
from sklearn.metrics import accuracy_score

PERF_FORMAT_STRING = "\
\tAccuracy: {:>0.{display_precision}f}\tPrecision: {:>0.{display_precision}f}\t\
Recall: {:>0.{display_precision}f}\tF1: {:>0.{display_precision}f}\tF2: {:>0.{display_precision}f}"
RESULTS_FORMAT_STRING = "\tTotal predictions: {:4d}\tTrue positives: {:4d}\tFalse positives: {:4d}\
\tFalse negatives: {:4d}\t True negatives: {:4d}"

#The formspring dataset was cleaned and labeling was converted to binary form using
#extract.py script and loaded into pickle files
words_file = "my_dataset.pkl"
labels_file = "my_feature_list.pkl"
word_data = pickle.load( open(words_file, "rb"))
labels_data = pickle.load( open(labels_file, "rb") )
#convert labels_data to integers
labels_data = [int(i) for i in labels_data]

bully_df= pd.DataFrame({'text': word_data,'flag': labels_data})
#bully_df[bully_df.flag ==0].shape

#get the subset with only bullying comments
df_subset = bully_df[bully_df.flag ==1]
#print(df_subset.shape)

#merge the data frames to increase the ratio of bully comments
frames_to_cat = [bully_df, df_subset]
df_final = pd.concat(frames_to_cat)

## converting dataframe to list
#print(dir(df_final))
word_data = df_final['text'].tolist()
labels_data = df_final['flag'].tolist()
#print(word_data)


vectorizer = TfidfVectorizer(sublinear_tf=True, max_df=0.20, ngram_range = (1,2),
                             max_features = 100000, stop_words='english', use_idf=True)

#pprint.pprint(vectorizer.transform(features_train))

#features_train = vectorizer.fit_transform(features_train)
#features_test  = vectorizer.transform(features_test)
#pprint.pprint(vectorizer.get_feature_names())

clf = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(15,4), random_state=1)
pipeline = Pipeline([('tf_idf', vectorizer),
                     ('classifier', clf)
          ])
kf = KFold(n_splits = 12, random_state = 42, shuffle = True)
true_negatives = 0
false_negatives = 0
true_positives = 0
false_positives = 0

for train_idx, test_idx in kf.split(word_data, labels_data):
    print(len(train_idx), len(test_idx))
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
    predictions = pipeline.predict(features_test)
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
