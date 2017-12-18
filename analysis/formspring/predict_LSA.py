#!/usr/bin/python

import pickle
import time
import numpy
numpy.random.seed(42)
import pprint
# metric model to evaluate the model performance
from sklearn import metrics
from sklearn.decomposition import TruncatedSVD
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer


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
features_train, features_test, labels_train, labels_test = model_selection.train_test_split(word_data,
                                                            labels_data, test_size=0.1, random_state=42)

"""
features_train = features_train[:2]
labels_train   = labels_train[:2]
features_test = features_test[:2]
labels_test = labels_test[:2]
"""
#print(features_train[:5])
### your code goes here
from sklearn.svm import SVC, LinearSVC
from sklearn.naive_bayes import  MultinomialNB
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier

vectorizer = TfidfVectorizer(sublinear_tf=True, max_df=0.30, ngram_range = (1,2),
                             max_features = 100000, stop_words='english')

#pprint.pprint(vectorizer.transform(features_train))

features_train = vectorizer.fit_transform(features_train)
features_test  = vectorizer.transform(features_test)
#pprint.pprint(vectorizer.get_feature_names())

#print("  Actual number of tfidf features: %d" % features_train.get_shape()[1])
print("actual features", features_train.get_shape())

print("\nPerforming dimensionality reduction using LSA")
t0 = time.time()

# Project the tfidf vectors onto the first N principal components.
# Though this is significantly fewer features than the original tfidf vector,
# they are stronger features, and the accuracy is higher.
svd = TruncatedSVD(500)
lsa = make_pipeline(svd, Normalizer(copy=False))

# Run SVD on the training data, then project the training data.
X_train_lsa = lsa.fit_transform(features_train)

print("  done in %.3fsec" % (time.time() - t0))

explained_variance = svd.explained_variance_ratio_.sum()
print("  Explained variance of the SVD step: {}%".format(int(explained_variance * 100)))


# Now apply the transformations to the test data as well.
X_test_lsa = lsa.transform(features_test)

from sklearn import tree
from sklearn.metrics import accuracy_score

#clf = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(15,4), random_state=1)
#clf = SVC()
clf = LinearSVC()
#clf = SGDClassifier()
#clf = LogisticRegression()
#clf = tree.DecisionTreeClassifier()
#clf = MultinomialNB()
#clf = RandomForestClassifier(n_estimators=100)
clf = clf.fit(X_train_lsa, labels_train)
pred =  clf.predict(X_test_lsa)
#accuracy = accuracy_score(pred,labels_test)
#print("accuracy is: ", round(accuracy,3))
#[print(type(int(item))) for item in pred]

# testing accuracy
print("accuracy is: ", metrics.accuracy_score(labels_test, pred))
print(metrics.classification_report(labels_test, pred))

true_negatives = 0
false_negatives = 0
true_positives = 0
false_positives = 0
for prediction, truth in zip(pred, labels_test):
    prediction, truth = int(prediction), int(truth)
    if prediction == 0 and truth == 0:
        true_negatives += 1
    elif prediction == 0 and truth == 1:
        false_negatives += 1
    elif prediction == 1 and truth == 0:
        false_positives += 1
    elif prediction == 1 and truth == 1:
        true_positives += 1
    else:
        print("Warning: Found a predicted label not == 0 or 1.")
        print("All predictions should take value 0 or 1.")
        print("Evaluating performance for processed predictions:")
        break
try:
    total_predictions = true_negatives + false_negatives + false_positives + true_positives
    accuracy = 1.0*(true_positives + true_negatives)/total_predictions
    precision = 1.0*true_positives/(true_positives+false_positives)
    recall = 1.0*true_positives/(true_positives+false_negatives)
    f1 = 2.0 * true_positives/(2*true_positives + false_positives+false_negatives)
    f2 = (1+2.0*2.0) * precision*recall/(4*precision + recall)
    print(clf)
    print(PERF_FORMAT_STRING.format(accuracy, precision, recall, f1, f2, display_precision = 5))
    print(RESULTS_FORMAT_STRING.format(total_predictions, true_positives, false_positives, false_negatives, true_negatives))
    print("")
except:
    print("Got a divide by zero when trying out:", clf)
    print("Precision or recall may be undefined due to a lack of true positive predicitons.")



#for rank in range(len(clf.feature_importances_)):
    #if clf.feature_importances_[rank] > 0.2:
    #print(rank, clf.feature_importances_[rank])
#    pass
#print(vectorizer.get_feature_names()[5591])
#print(vectorizer.get_feature_names()[5752])
