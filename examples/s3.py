"""
Example script showing how to write data to S3 and how to load data from S3 into pandas.

To start connecting to AWS you'll need to have added credentials to ~/.aws/credentials.
For problems debugging setup reference: http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html.

Boto3 API docs: boto3.readthedocs.io/en/latest/reference
"""
from io import StringIO

import boto3
import os
import yaml
import pandas as pd

PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG = yaml.load(open(PARENT_DIR + '/config.yml', 'r'))

# S3 Tutorial: https://dluo.me/s3databoto3

session = boto3.session.Session(profile_name=CONFIG.get('aws').get('user_name'))
s3 = session.client('s3')
bucket_key = CONFIG.get('s3').get('test_bucket_key')
bucket_name = CONFIG.get('s3').get('test_bucket_name')


# Commented out as this has already been written to S3
# s3 = session.resource('s3')
# my_bucket = s3.Bucket(bucket_name)
# for filename in os.listdir(PARENT_DIR + '/data/wikipedia-detox/comments_article_2015'):
#     my_bucket.upload_file(BASE_DIR + '/comments_article_2015/' + filename, Key=bucket_key + '/{0}'.format(filename))
#     print('Uploading {0}'.format(filename))

obj = s3.get_object(Bucket=bucket_name, Key=bucket_key + '/chunk_0.tsv')['Body']
obj = obj.read().decode('utf-8')
df = pd.read_csv(StringIO(obj), delimiter='\t')
print(df.head())

# If you'd like to download the obj to a local file, use the following
# s3_client.download_file(s3_bucket, s3_key, local_file)