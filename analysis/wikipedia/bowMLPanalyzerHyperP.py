# import necessary tools
import time
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer

from sklearn.pipeline import Pipeline
#from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV

from sklearn import metrics
from sklearn.neural_network import MLPClassifier

start_time = time.time()


# load data into DataFrame
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

print('This is your DataFrame:\n')
print(comments.head())
print('These are the head of the comments classified as an attack\n')
print(comments.query('attack')['comment'].head())

# create y which is the outcome label the model has to learn
y = comments['attack']

'''
split the dataframe into training and testing data
split the features X (that are the comment column, comments['comment'])
and the label y (attack, comments['attack']) based on a given test size such as 0.33 (33%)
random state, so we can have repeatable results when we run the code again
the function will take 33% of rows to be marked as test data and move them from the training data.
the test data is later used to see how the model has learned

The resulting data from train_test_split() are:
training data as X_train, training labels as y_train,
testing data as X_test and testing labels as y_test
'''

X_train, X_test, y_train, y_test = train_test_split(comments['comment'], y, test_size=0.33, random_state=53)


# create count vectorizer that turn the text into a bag-of-words vectors
# each tokens acts as a feature for the machine learning classification problem

max_features = (5000, 10000, 30000)


solver = ('lbfgs', 'adam')
alpha_space = np.logspace(0, -5, 6)
hidden_layer_sizes = (15, 4)


param_grid = {
    'vec__max_features': max_features,
    'vec__ngram_range': ((1, 5),),
    'vec__analyzer': ('char',),
    'clf__solver': solver,
    'clf__alpha': alpha_space,
    'clf__hidden_layer_sizes': hidden_layer_sizes,
}


# Setup the pipeline
steps = [('vec', CountVectorizer()),
         ('clf', MLPClassifier())]

pipeline = Pipeline(steps)

load_time = time.time()

# Instantiate the GridSearchCV object: cv
cv = GridSearchCV(pipeline, param_grid, cv=12)

# Fit to the training set
cv.fit(X_train, y_train)

build_time = time.time()

# Predict the labels of the test set: y_pred
y_pred = cv.predict(X_test)

# Compute and print metrics
print("Accuracy: {}".format(cv.score(X_test, y_test)))
print("Tuned Model Parameters: {}".format(cv.best_params_))
print(metrics.classification_report(y_test, y_pred))
eval_time = time.time()

print("Times: %0.3f sec loading, %0.3f sec building, %0.3f sec evaluation" % (load_time - start_time, build_time - load_time, eval_time - build_time,))
print("Total time: %0.3f seconds" % (eval_time - start_time))
