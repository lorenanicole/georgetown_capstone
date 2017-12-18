# Formspring Data Text Classification
This is a machine learning project used to identify aggressive comments in online communities. I have used formspring data (https://www.kaggle.com/swetaagrawal/formspring-data-for-cyberbullying-detection) as the input text data. 

The formspring data looked very messy and I spent quite some time in clean up and structuring of this data. The data cleaning and text normalization is done uisng the script "extract.py". This is a highly imbalanced classification with ~6 % cases of cyberbullying. Given below is the breakdown of work division implemented by various scripts for text calssification.

## `extract.py` cleans, normalizes and loads the data into pickle files

## `predict.py` carries our some feature optimization, text vectorization and test various model families

## `predict_LSA.py` applies SVD for feature reduction

## `predict_KFoldOverSample.py` adds additional bullying comments to improve the class imbalance 

## Best statistics currently obtained from the oversampled data: [precision:0.82, recall:0.94, F1:0.86] 
