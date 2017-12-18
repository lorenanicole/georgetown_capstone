## This file extracts, cleans the text, and also converts the response of
## The Amazon Turks into binary form, based on majority of responses
## The comments and labels are written out to pickle files.

from nltk.stem.snowball import SnowballStemmer
from nltk.stem import WordNetLemmatizer
import string
import re
import pickle

def read_file(path):
    # First open the file
    with open(path, 'rt') as f:
        #skip first line
        f.readline()
        #next(f)
        # read files line by line
        lines = f.readlines()
        #lines = f.read().split("\n")
    #print(lines[0])
    return lines

def get_comments_label(path):
    lines = read_file(path)
    labels = []
    comments = []
    counter = 0
    for line in lines:
    #if counter < 500:
        ### Let us process the comment first
        processed_comment = parse_comments(line)
        ### check for labeling only if the processed_comment is not None
        if processed_comment:
            ### Now lets look at the labeling
            respons_re = re.compile(r'(?:No|Yes)\s(?:\d|None)')
            #mo = respons_re.search(lines[1])
            mo = respons_re.findall(line)
            ### let us count the comments if more than two amazon turks have responded
            ### the same way
            count_yes = 0
            count_no = 0
            for item in mo:
                #print(item)
                if re.search(r'Yes',item):
                    count_yes += 1
                elif re.search(r'No',item):
                    count_no += 1
            if (count_yes >= 2):
                labels.append("1")
                comments.append(processed_comment)
            elif (count_no >= 2):
                labels.append("0")
                comments.append(processed_comment)
            else:
                #   print(mo, " response too small or null")
                pass
        counter += 1

    return comments, labels


def parse_comments(comment):
    #get the comment encolsed by Q: and No/Yes d
    #print(len(comment))
    filter1 = re.search('Q:(.*?)(?:No|Yes)\s(?:\d|None)', comment)
    if filter1:
        #remove the repetitive term "<br>A:" from filter1
        filter2 = re.sub('<br>A:','',filter1.group(1))
        #remove punctuation
        #this execution is slightly differently in python 2.7
        translator = str.maketrans('','',string.punctuation)
        text_string = filter2.translate(translator)
        #print(text_string)
        ### split the text string into individual words, stem each word,
        ### and append the stemmed word to words (make sure there's a single
        ### space between each stemmed word)
        words = ""
        stemmer = SnowballStemmer("english")
        wordnet_lemmatizer = WordNetLemmatizer()
        for text in text_string.split():
            #print stemmer.stem(text)
            words += stemmer.stem(text) + " "
            #words += wordnet_lemmatizer.lemmatize(text) + " "
        return words
    else:
        return None

DATASET_PICKLE_FILENAME = "my_dataset.pkl"
FEATURE_LIST_FILENAME = "my_feature_list.pkl"

def dump_classifier_and_data(datasets, feature_list):
    with open(DATASET_PICKLE_FILENAME, "wb") as dataset_outfile:
        pickle.dump(datasets, dataset_outfile)

    with open(FEATURE_LIST_FILENAME, "wb") as featurelist_outfile:
        pickle.dump(feature_list, featurelist_outfile)


if __name__ == '__main__':
    comments, labels = get_comments_label("formspring_data.csv")
    #print(type(comments[0]))
    #for comment, label in zip(comments, labels):
    #    print(comment," and the label is: ", label)
    print(len(comments), len(labels))
    dump_classifier_and_data(comments, labels)
