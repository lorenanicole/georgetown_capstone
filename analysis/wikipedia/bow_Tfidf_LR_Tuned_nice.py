##########################################################################
# Imports
##########################################################################

import time
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
from sklearn import metrics
from sklearn import cross_validation
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.linear_model import LogisticRegression

##########################################################################
# Logistic Regression Classification
##########################################################################

start_time = time.time()

# Load the dataset

comments = pd.read_csv('attack_annotated_comments.tsv', sep='\t', index_col=0)
annotations = pd.read_csv('attack_annotations.tsv', sep='\t')

# print the # of unique rev_id
print('There are', len(annotations['rev_id'].unique()), 'unique rev_id')

# labels a comment as an attack if the majority of annotators did so
labels = annotations.groupby('rev_id')['attack'].mean() > 0.5

# insert labels in comments
comments['attack'] = labels

# Parsing: remove newline and tab tokens
comments['comment'] = comments['comment'].apply(lambda x: x.replace("NEWLINE_TOKEN", " "))
comments['comment'] = comments['comment'].apply(lambda x: x.replace("TAB_TOKEN", " "))

# Presentation

print('This is your DataFrame:\n')
print(comments.head())
print('These are the head of the comments classified as an attack\n')
print(comments.query('attack')['comment'].head())

# create y which is the outcome label the model has to learn
X = comments['comment']
y = comments['attack']

# Get training and testing splits
X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.33, random_state=53)

# Setup the pipeline
steps = [('vec', CountVectorizer(analyzer='char', ngram_range=(1, 5), max_features=50000)),
         ('tfidf', TfidfTransformer(norm='l2', sublinear_tf=True)),
         ('clf', LogisticRegression(C=10))]

pipeline = Pipeline(steps)

load_time = time.time()

# Fit the training data to the model
pipeline.fit(X_train, y_train)

build_time = time.time()

print(pipeline)


# Make predictions: predict the labels of the test set (y_pred)
expected = y_test
predicted = pipeline.predict(X_test)


# Evaluate the predictions: compute and print metrics
print("Accuracy: {}".format(pipeline.score(X_test, expected)))
print()
print(metrics.confusion_matrix(expected, predicted))
print()
print(metrics.classification_report(expected, predicted))
print()

eval_time = time.time()

print("Times: %0.3f sec loading, %0.3f sec building, %0.3f sec evaluation" % (load_time - start_time, build_time - load_time, eval_time - build_time,))
print("Total time: %0.3f seconds" % (eval_time - start_time))
