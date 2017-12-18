# georgetown_capstone

This project talks about: https://meta.wikimedia.org/wiki/Research:Detox/Data_Release


You can find the files related to wiki Detox project at: https://figshare.com/articles/Wikipedia_Talk_Labels_Personal_Attacks/4054689

attack: attack_annotated_comments.tsv(55.43 MB)
        attack_annotations.tsv(44.59 MB)
        
        
I have used as an example the 2 files from wikidetox attack_annotated_comments.tsv and attack_annotations.tsv

The other files needed are already in the repository

Be sure to downloads all the needed files before!!


Exploratory Phase (Exploratory Data Analysis)

Understand Transformers: See_how_Fit_transform_works.ipynb

Length of comments and dictionary: EDA.ipynb


Use of Classifiers:

Simple bow with Naive Bayes: bowNBanalyzer.ipynb

Use of Tfidf Transformer with Naive Bayes: tfidfNBanalyzer.ipynb

Use of MultiLayerPerceptron: MLP_classifier.ipynb

Use of Logistic Regression: tfidfLRanalyzer.ipynb

Use of the Pipeline for Logistic Regression (LR) and use of an external set example as holdout test to print Machine Learning prediction Vs Human Labeling for a comment: bowTfidfLR_model01.ipynb

Naive Bayes tuned after GridSearchCV (Hyperparameters): bow_Tfidf_NB_Tuned.ipynb

Hyperparameter tuning for Naive Bayes: bowNBanalyzer132.py (Python File,not notebook)

Hyperparameter tuning for Logistic Regression: bowTfidfLRanalyzerPipeline.py

Hyperparameter tuning for MLP: bowMLPanalyzerHyperP.py

Example of Logistic Regression Pipeline after Hyperparameter tuning: bow_Tfidf_LR_Tuned_nice.py

Example of Words Visualization: Word_Viz.ipynb

Boxplot model comparison: Comparison_model.ipynb

Analyzing (LR) external datasets from scraped data (reddit communities, politics, soccer, video games) and heatmap with Yellobrick: LR_ExternalHoldouts.ipynb
