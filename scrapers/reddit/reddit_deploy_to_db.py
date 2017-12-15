from datetime import datetime
import json
import os

import boto3
import psycopg2
import yaml
from psycopg2._psycopg import IntegrityError

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = yaml.load(open(PARENT_DIR + '/config.yml', 'r'))
SUBREDDITS = ['politics', 'Leagueoflegends', 'AskReddit', 'soccer']

class Query(object):

    engine_string = 'postgresql+psycopg2://{0}:{1}:{2}:{3}/{4}'

    def __init__(self, db_config, is_read_only=False):
        '''
        Any config info specified in the config (see CONFIG above) will be added as an attribute to the Query class
        when instantiated. Permits reconnection (see execute method implementations below) if necessary.
        '''
        for key in db_config:
            setattr(self, key, db_config[key])
        self.is_read_only = is_read_only

        self.__connect__()

    def __connect__(self):
        self.connection = psycopg2.connect(host=self.url,
                                           user=self.user_name,
                                           port=self.port,
                                           password=self.password,
                                           dbname=self.db_name)
        self.connection.set_session(readonly=self.is_read_only, autocommit=True)
        self.cursor = self.connection.cursor()


class Row(object):
    def to_insert_sql(self):
        table_name = (type(self).__name__).lower() + 's'
        properties = ','.join(prop for prop in vars(self).keys())
        values = ','.join('%s' for time in range(0, len(vars(self).keys())))
        return '''
        INSERT INTO {0}(
            {1}
        )
        VALUES ({2});
        '''.format(table_name, properties, values), list(vars(self).values())


class SubReddit(Row):
    def __init__(self, data):
        self.name = data.get('name').lower()


class Author(Row):
    def __init__(self, data):
        self.name = data.get('name')


class Comment(Row):
        def __init__(self,data):
                self.permalink = data.get('permalink', '')
                self.id = data.get('id', '')
                self.author = data.get('author', '')
                self.subreddit = data.get('subreddit').lower()
                self.subreddit_id = data.get('subreddit_id', '')
                self.name = data.get('name', '')
                self.parent_id = data.get('parent_id', '')
                self.depth = int(data.get('depth',0))
                self.body = data.get('body', '')
                self.score = int(data.get('score', 0))
                self.ups = int(data.get('ups', 0))
                self.downs = int(data.get('downs', 0))
                self.controversiality = int(data.get('controversiality', 0))
                self.user_reports = ','.join(u for u in data.get('user_reports')) if isinstance(data.get('user_reports', ''), list) else data.get('user_reports', '')
                self.created_utc = int(data.get('created_utc',0))
                self.label = int(data.get('label', 0))


class Submission(Row):
        def __init__(self,data):
                self.permalink = data.get('permalink', '')
                self.id = data.get('id', '')
                self.name = data.get('name', '')
                self.title = data.get('title', '')
                self.author = data.get('author', '')
                self.subreddit = data.get('subreddit', '').lower()
                self.user_reports = ','.join(u for u in data.get('user_reports')) if isinstance(data.get('user_reports', ''), list) else data.get('user_reports', '')
                self.created_utc = int(data.get('created_utc',0))
                self.downs = int(data.get('downs', 0))
                self.url = data.get('url', '')
                self.ups = int(data.get('ups', 0))
                self.comment_limit = int(data.get('comment_limit', 0))
                self.score = int(data.get('score', 0))
                self.score = float(data.get('upvote_ratio', 0.0))
                self.over_18 = bool(data.get('over_18', False))
                self.brand_safe = data.get('brand_safe', True)
                self.num_comments = int(data.get('num_comments', 0))

if __name__ == '__main__':

    q = Query(CONFIG.get('db'))
    # 1. If tables don't exist, create table
    create_table_sql = {
        'authors': '''CREATE TABLE authors (name VARCHAR(250) NOT NULL UNIQUE);''',
        'subreddits': '''CREATE TABLE subreddits (name VARCHAR(250) NOT NULL UNIQUE);''',
        'comments': '''
    CREATE TABLE comments(
                        permalink VARCHAR(800) NOT NULL UNIQUE,
                        id VARCHAR(250) NOT NULL,
                        author VARCHAR(250) NOT NULL,
                        subreddit VARCHAR(25) NOT NULL,
                        subreddit_id VARCHAR(25) NOT NULL,
                        name VARCHAR(25) NOT NULL,
                        parent_id VARCHAR(25),
                        depth INTEGER DEFAULT 0,
                        body TEXT NOT NULL,
                        score INTEGER DEFAULT 0,
                        ups INTEGER DEFAULT 0,
                        downs INTEGER DEFAULT 0,
                        controversiality INTEGER DEFAULT 0,
                        user_reports TEXT,
                        created_utc INTEGER NOT NULL,
                        label INTEGER DEFAULT 0,
                        FOREIGN KEY (author) REFERENCES authors (name),
                        FOREIGN KEY (subreddit) REFERENCES subreddits (name)
                        );
    ''',
        'submissions': '''
    CREATE TABLE submissions (permalink VARCHAR(800) NOT NULL UNIQUE,
                          id VARCHAR(250) NOT NULL,
                          name VARCHAR(25) NOT NULL,
                          title text NOT NULL,
                          author VARCHAR(250) NOT NULL,
                          subreddit VARCHAR(250) NOT NULL,
                          user_reports TEXT,
                          created_utc INTEGER NOT NULL,
                          downs INTEGER DEFAULT 0,
                          url VARCHAR(250),
                          ups INTEGER DEFAULT 0,
                          comment_limit INTEGER DEFAULT 0,
                          score INTEGER DEFAULT 0,
                          upvote_ratio NUMERIC,
                          over_18 BOOLEAN,
                          brand_safe BOOLEAN,
                          num_comments INTEGER DEFAULT 0,
                        FOREIGN KEY (author) REFERENCES authors (name),
                        FOREIGN KEY (subreddit) REFERENCES subreddits (name)
                          );
                          '''
    }

    # for table, sql in create_table_sql.items():
    #     print('Creating table {0}'.format(table))
    #     try:
    #         q.cursor.execute('DROP TABLE {} cascade;'.format(table))
    #         q.cursor.execute(sql)
    #     except Exception as e:
    #         print(e)
    #         print('Cannot make table {}'.format(table))

#     for table, sql in create_table_sql.items():
#         print('Check if table {0} exists'.format(table))
#         try:
#             q.cursor.execute('''
# SELECT EXISTS (
#    SELECT 1
#    FROM   information_schema.tables
#    WHERE  table_schema = 'public'
#    AND    table_name = '{}'
#    );
#    '''.format(table))
#             rows = q.cursor.fetchall()
#             print(rows)
#         except Exception as e:
#             print(e)

    # 2. Download raw data
    bucket_name = CONFIG.get('s3').get('bucket_name')
    session = boto3.session.Session(
        aws_access_key_id=CONFIG.get('aws').get('aws_access_key_id'),
        aws_secret_access_key=CONFIG.get('aws').get('aws_secret_access_key')
    )

    s3 = session.client('s3')
    bucket_keys = s3.list_objects_v2(Bucket=bucket_name)

    keys = ['reddit/2017-11-02/AskReddit_authors.json', 'reddit/2017-11-02/AskReddit_comments.json', 'reddit/2017-11-02/AskReddit_submissions.json', 'reddit/2017-11-02/Leagueoflegends_authors.json', 'reddit/2017-11-02/Leagueoflegends_comments.json', 'reddit/2017-11-02/Leagueoflegends_submissions.json', 'reddit/2017-11-02/politics_authors.json', 'reddit/2017-11-02/politics_comments.json', 'reddit/2017-11-02/politics_submissions.json', 'reddit/2017-11-02/soccer_authors.json', 'reddit/2017-11-02/soccer_comments.json', 'reddit/2017-11-02/soccer_submissions.json', 'reddit/2017-11-03/AskReddit_authors.json', 'reddit/2017-11-03/AskReddit_comments.json', 'reddit/2017-11-03/AskReddit_submissions.json', 'reddit/2017-11-03/Leagueoflegends_authors.json', 'reddit/2017-11-03/Leagueoflegends_comments.json', 'reddit/2017-11-03/Leagueoflegends_submissions.json', 'reddit/2017-11-03/politics_authors.json', 'reddit/2017-11-03/politics_comments.json', 'reddit/2017-11-03/politics_submissions.json', 'reddit/2017-11-03/soccer_authors.json', 'reddit/2017-11-03/soccer_comments.json', 'reddit/2017-11-03/soccer_submissions.json', 'reddit/2017-11-04/AskReddit_authors.json', 'reddit/2017-11-04/AskReddit_comments.json', 'reddit/2017-11-04/AskReddit_submissions.json', 'reddit/2017-11-04/Leagueoflegends_authors.json', 'reddit/2017-11-04/Leagueoflegends_comments.json', 'reddit/2017-11-04/Leagueoflegends_submissions.json', 'reddit/2017-11-04/politics_authors.json', 'reddit/2017-11-04/politics_comments.json', 'reddit/2017-11-04/politics_submissions.json', 'reddit/2017-11-04/soccer_authors.json', 'reddit/2017-11-04/soccer_comments.json', 'reddit/2017-11-04/soccer_submissions.json', 'reddit/2017-11-07/AskReddit_authors.json', 'reddit/2017-11-07/AskReddit_comments.json', 'reddit/2017-11-07/AskReddit_submissions.json', 'reddit/2017-11-07/Leagueoflegends_authors.json', 'reddit/2017-11-07/Leagueoflegends_comments.json', 'reddit/2017-11-07/Leagueoflegends_submissions.json', 'reddit/2017-11-07/politics_authors.json', 'reddit/2017-11-07/politics_comments.json', 'reddit/2017-11-07/politics_submissions.json', 'reddit/2017-11-07/soccer_authors.json', 'reddit/2017-11-07/soccer_comments.json', 'reddit/2017-11-07/soccer_submissions.json', 'reddit/2017-11-08/AskReddit_authors.json', 'reddit/2017-11-08/AskReddit_comments.json', 'reddit/2017-11-08/AskReddit_submissions.json', 'reddit/2017-11-08/Leagueoflegends_authors.json', 'reddit/2017-11-08/Leagueoflegends_comments.json', 'reddit/2017-11-08/Leagueoflegends_submissions.json', 'reddit/2017-11-08/politics_authors.json', 'reddit/2017-11-08/politics_comments.json', 'reddit/2017-11-08/politics_submissions.json', 'reddit/2017-11-08/soccer_authors.json', 'reddit/2017-11-08/soccer_comments.json', 'reddit/2017-11-08/soccer_submissions.json', 'reddit/2017-11-09/AskReddit_authors.json', 'reddit/2017-11-09/AskReddit_comments.json', 'reddit/2017-11-09/AskReddit_submissions.json', 'reddit/2017-11-09/Leagueoflegends_authors.json', 'reddit/2017-11-09/Leagueoflegends_comments.json', 'reddit/2017-11-09/Leagueoflegends_submissions.json', 'reddit/2017-11-09/politics_authors.json', 'reddit/2017-11-09/politics_comments.json', 'reddit/2017-11-09/politics_submissions.json', 'reddit/2017-11-09/soccer_authors.json', 'reddit/2017-11-09/soccer_comments.json', 'reddit/2017-11-09/soccer_submissions.json', 'reddit/2017-11-14/AskReddit_authors.json', 'reddit/2017-11-14/AskReddit_comments.json', 'reddit/2017-11-14/AskReddit_submissions.json', 'reddit/2017-11-14/Leagueoflegends_authors.json', 'reddit/2017-11-14/Leagueoflegends_comments.json', 'reddit/2017-11-14/Leagueoflegends_submissions.json', 'reddit/2017-11-14/politics_authors.json', 'reddit/2017-11-14/politics_comments.json', 'reddit/2017-11-14/politics_submissions.json', 'reddit/2017-11-14/soccer_authors.json', 'reddit/2017-11-14/soccer_comments.json', 'reddit/2017-11-14/soccer_submissions.json', 'reddit/2017-11-15/AskReddit_authors.json', 'reddit/2017-11-15/AskReddit_comments.json', 'reddit/2017-11-15/AskReddit_submissions.json', 'reddit/2017-11-15/Leagueoflegends_authors.json', 'reddit/2017-11-15/Leagueoflegends_comments.json', 'reddit/2017-11-15/Leagueoflegends_submissions.json', 'reddit/2017-11-15/politics_authors.json', 'reddit/2017-11-15/politics_comments.json', 'reddit/2017-11-15/politics_submissions.json', 'reddit/2017-11-15/soccer_authors.json', 'reddit/2017-11-15/soccer_comments.json', 'reddit/2017-11-15/soccer_submissions.json', 'reddit/2017-11-16/AskReddit_authors.json', 'reddit/2017-11-16/AskReddit_comments.json', 'reddit/2017-11-16/AskReddit_submissions.json', 'reddit/2017-11-16/Leagueoflegends_authors.json', 'reddit/2017-11-16/Leagueoflegends_comments.json', 'reddit/2017-11-16/Leagueoflegends_submissions.json', 'reddit/2017-11-16/politics_authors.json', 'reddit/2017-11-16/politics_comments.json', 'reddit/2017-11-16/politics_submissions.json', 'reddit/2017-11-16/soccer_authors.json', 'reddit/2017-11-16/soccer_comments.json', 'reddit/2017-11-16/soccer_submissions.json', 'reddit/2017-11-17/AskReddit_authors.json', 'reddit/2017-11-17/AskReddit_comments.json', 'reddit/2017-11-17/AskReddit_submissions.json', 'reddit/2017-11-17/Leagueoflegends_authors.json', 'reddit/2017-11-17/Leagueoflegends_comments.json', 'reddit/2017-11-17/Leagueoflegends_submissions.json', 'reddit/2017-11-17/politics_authors.json', 'reddit/2017-11-17/politics_comments.json', 'reddit/2017-11-17/politics_submissions.json', 'reddit/2017-11-17/soccer_authors.json', 'reddit/2017-11-17/soccer_comments.json', 'reddit/2017-11-17/soccer_submissions.json', 'reddit/2017-11-18/AskReddit_authors.json', 'reddit/2017-11-18/AskReddit_comments.json', 'reddit/2017-11-18/AskReddit_submissions.json', 'reddit/2017-11-18/Leagueoflegends_authors.json', 'reddit/2017-11-18/Leagueoflegends_comments.json', 'reddit/2017-11-18/Leagueoflegends_submissions.json', 'reddit/2017-11-18/politics_authors.json', 'reddit/2017-11-18/politics_comments.json', 'reddit/2017-11-18/politics_submissions.json', 'reddit/2017-11-18/soccer_authors.json', 'reddit/2017-11-18/soccer_comments.json', 'reddit/2017-11-18/soccer_submissions.json', 'reddit/2017-11-21/AskReddit_authors.json', 'reddit/2017-11-21/AskReddit_comments.json', 'reddit/2017-11-21/AskReddit_submissions.json', 'reddit/2017-11-21/Leagueoflegends_authors.json', 'reddit/2017-11-21/Leagueoflegends_comments.json', 'reddit/2017-11-21/Leagueoflegends_submissions.json', 'reddit/2017-11-21/politics_authors.json', 'reddit/2017-11-21/politics_comments.json', 'reddit/2017-11-21/politics_submissions.json', 'reddit/2017-11-21/soccer_authors.json', 'reddit/2017-11-21/soccer_comments.json', 'reddit/2017-11-21/soccer_submissions.json', 'reddit/2017-11-22/AskReddit_authors.json', 'reddit/2017-11-22/AskReddit_comments.json', 'reddit/2017-11-22/AskReddit_submissions.json', 'reddit/2017-11-22/Leagueoflegends_authors.json', 'reddit/2017-11-22/Leagueoflegends_comments.json', 'reddit/2017-11-22/Leagueoflegends_submissions.json', 'reddit/2017-11-22/politics_authors.json', 'reddit/2017-11-22/politics_comments.json', 'reddit/2017-11-22/politics_submissions.json', 'reddit/2017-11-22/soccer_authors.json', 'reddit/2017-11-22/soccer_comments.json', 'reddit/2017-11-22/soccer_submissions.json', 'reddit/2017-11-23/AskReddit_authors.json', 'reddit/2017-11-23/AskReddit_comments.json', 'reddit/2017-11-23/AskReddit_submissions.json', 'reddit/2017-11-23/Leagueoflegends_authors.json', 'reddit/2017-11-23/Leagueoflegends_comments.json', 'reddit/2017-11-23/Leagueoflegends_submissions.json', 'reddit/2017-11-23/politics_authors.json', 'reddit/2017-11-23/politics_comments.json', 'reddit/2017-11-23/politics_submissions.json', 'reddit/2017-11-23/soccer_authors.json', 'reddit/2017-11-23/soccer_comments.json', 'reddit/2017-11-23/soccer_submissions.json', 'reddit/2017-11-24/AskReddit_authors.json', 'reddit/2017-11-24/AskReddit_comments.json', 'reddit/2017-11-24/AskReddit_submissions.json', 'reddit/2017-11-24/Leagueoflegends_authors.json', 'reddit/2017-11-24/Leagueoflegends_comments.json', 'reddit/2017-11-24/Leagueoflegends_submissions.json', 'reddit/2017-11-24/politics_authors.json', 'reddit/2017-11-24/politics_comments.json', 'reddit/2017-11-24/politics_submissions.json', 'reddit/2017-11-24/soccer_authors.json', 'reddit/2017-11-24/soccer_comments.json', 'reddit/2017-11-24/soccer_submissions.json', 'reddit/2017-11-25/AskReddit_authors.json', 'reddit/2017-11-25/AskReddit_comments.json', 'reddit/2017-11-25/AskReddit_submissions.json', 'reddit/2017-11-25/Leagueoflegends_authors.json', 'reddit/2017-11-25/Leagueoflegends_comments.json', 'reddit/2017-11-25/Leagueoflegends_submissions.json', 'reddit/2017-11-25/politics_authors.json', 'reddit/2017-11-25/politics_comments.json', 'reddit/2017-11-25/politics_submissions.json', 'reddit/2017-11-25/soccer_authors.json', 'reddit/2017-11-25/soccer_comments.json', 'reddit/2017-11-25/soccer_submissions.json', 'reddit/2017-11-26/AskReddit_authors.json', 'reddit/2017-11-26/AskReddit_comments.json', 'reddit/2017-11-26/AskReddit_submissions.json', 'reddit/2017-11-26/Leagueoflegends_authors.json', 'reddit/2017-11-26/Leagueoflegends_comments.json', 'reddit/2017-11-26/Leagueoflegends_submissions.json', 'reddit/2017-11-26/politics_authors.json', 'reddit/2017-11-26/politics_comments.json', 'reddit/2017-11-26/politics_submissions.json', 'reddit/2017-11-26/soccer_authors.json', 'reddit/2017-11-26/soccer_comments.json', 'reddit/2017-11-26/soccer_submissions.json', 'reddit/2017-11-27/AskReddit_authors.json', 'reddit/2017-11-27/AskReddit_comments.json', 'reddit/2017-11-27/AskReddit_submissions.json', 'reddit/2017-11-27/Leagueoflegends_authors.json', 'reddit/2017-11-27/Leagueoflegends_comments.json', 'reddit/2017-11-27/Leagueoflegends_submissions.json', 'reddit/2017-11-27/politics_authors.json', 'reddit/2017-11-27/politics_comments.json', 'reddit/2017-11-27/politics_submissions.json', 'reddit/2017-11-27/soccer_authors.json', 'reddit/2017-11-27/soccer_comments.json', 'reddit/2017-11-27/soccer_submissions.json', 'reddit/2017-11-28/AskReddit_authors.json', 'reddit/2017-11-28/AskReddit_comments.json', 'reddit/2017-11-28/AskReddit_submissions.json', 'reddit/2017-11-28/Leagueoflegends_authors.json', 'reddit/2017-11-28/Leagueoflegends_comments.json', 'reddit/2017-11-28/Leagueoflegends_submissions.json', 'reddit/2017-11-28/politics_authors.json', 'reddit/2017-11-28/politics_comments.json', 'reddit/2017-11-28/politics_submissions.json', 'reddit/2017-11-28/soccer_authors.json', 'reddit/2017-11-28/soccer_comments.json', 'reddit/2017-11-28/soccer_submissions.json', 'reddit/2017-11-29/AskReddit_authors.json', 'reddit/2017-11-29/AskReddit_comments.json', 'reddit/2017-11-29/AskReddit_submissions.json', 'reddit/2017-11-29/Leagueoflegends_authors.json', 'reddit/2017-11-29/Leagueoflegends_comments.json', 'reddit/2017-11-29/Leagueoflegends_submissions.json', 'reddit/2017-11-29/politics_authors.json', 'reddit/2017-11-29/politics_comments.json', 'reddit/2017-11-29/politics_submissions.json', 'reddit/2017-11-29/soccer_authors.json', 'reddit/2017-11-29/soccer_comments.json', 'reddit/2017-11-29/soccer_submissions.json', 'reddit/2017-11-30/AskReddit_authors.json', 'reddit/2017-11-30/AskReddit_comments.json', 'reddit/2017-11-30/AskReddit_submissions.json', 'reddit/2017-11-30/Leagueoflegends_authors.json', 'reddit/2017-11-30/Leagueoflegends_comments.json', 'reddit/2017-11-30/Leagueoflegends_submissions.json', 'reddit/2017-11-30/politics_authors.json', 'reddit/2017-11-30/politics_comments.json', 'reddit/2017-11-30/politics_submissions.json', 'reddit/2017-11-30/soccer_authors.json', 'reddit/2017-11-30/soccer_comments.json', 'reddit/2017-11-30/soccer_submissions.json', 'reddit/2017-12-01/AskReddit_authors.json', 'reddit/2017-12-01/AskReddit_comments.json', 'reddit/2017-12-01/AskReddit_submissions.json', 'reddit/2017-12-01/Leagueoflegends_authors.json', 'reddit/2017-12-01/Leagueoflegends_comments.json', 'reddit/2017-12-01/Leagueoflegends_submissions.json', 'reddit/2017-12-01/politics_authors.json', 'reddit/2017-12-01/politics_comments.json', 'reddit/2017-12-01/politics_submissions.json', 'reddit/2017-12-01/soccer_authors.json', 'reddit/2017-12-01/soccer_comments.json', 'reddit/2017-12-01/soccer_submissions.json', 'reddit/2017-12-02/AskReddit_authors.json', 'reddit/2017-12-02/AskReddit_comments.json', 'reddit/2017-12-02/AskReddit_submissions.json', 'reddit/2017-12-02/Leagueoflegends_authors.json', 'reddit/2017-12-02/Leagueoflegends_comments.json', 'reddit/2017-12-02/Leagueoflegends_submissions.json', 'reddit/2017-12-02/politics_authors.json', 'reddit/2017-12-02/politics_comments.json', 'reddit/2017-12-02/politics_submissions.json', 'reddit/2017-12-02/soccer_authors.json', 'reddit/2017-12-02/soccer_comments.json', 'reddit/2017-12-02/soccer_submissions.json', 'reddit/2017-12-03/AskReddit_authors.json', 'reddit/2017-12-03/AskReddit_comments.json', 'reddit/2017-12-03/AskReddit_submissions.json', 'reddit/2017-12-03/Leagueoflegends_authors.json', 'reddit/2017-12-03/Leagueoflegends_comments.json', 'reddit/2017-12-03/Leagueoflegends_submissions.json', 'reddit/2017-12-03/politics_authors.json', 'reddit/2017-12-03/politics_comments.json', 'reddit/2017-12-03/politics_submissions.json', 'reddit/2017-12-03/soccer_authors.json', 'reddit/2017-12-03/soccer_comments.json', 'reddit/2017-12-03/soccer_submissions.json', 'reddit/2017-12-04/AskReddit_authors.json', 'reddit/2017-12-04/AskReddit_comments.json', 'reddit/2017-12-04/AskReddit_submissions.json', 'reddit/2017-12-04/Leagueoflegends_authors.json', 'reddit/2017-12-04/Leagueoflegends_comments.json', 'reddit/2017-12-04/Leagueoflegends_submissions.json', 'reddit/2017-12-04/politics_authors.json', 'reddit/2017-12-04/politics_comments.json', 'reddit/2017-12-04/politics_submissions.json', 'reddit/2017-12-04/soccer_authors.json', 'reddit/2017-12-04/soccer_comments.json', 'reddit/2017-12-04/soccer_submissions.json', 'reddit/2017-12-05/AskReddit_authors.json', 'reddit/2017-12-05/AskReddit_comments.json', 'reddit/2017-12-05/AskReddit_submissions.json', 'reddit/2017-12-05/Leagueoflegends_authors.json', 'reddit/2017-12-05/Leagueoflegends_comments.json', 'reddit/2017-12-05/Leagueoflegends_submissions.json', 'reddit/2017-12-05/politics_authors.json', 'reddit/2017-12-05/politics_comments.json', 'reddit/2017-12-05/politics_submissions.json', 'reddit/2017-12-05/soccer_authors.json', 'reddit/2017-12-05/soccer_comments.json', 'reddit/2017-12-05/soccer_submissions.json', 'reddit/2017-12-06/AskReddit_authors.json', 'reddit/2017-12-06/AskReddit_comments.json', 'reddit/2017-12-06/AskReddit_submissions.json', 'reddit/2017-12-06/Leagueoflegends_authors.json', 'reddit/2017-12-06/Leagueoflegends_comments.json', 'reddit/2017-12-06/Leagueoflegends_submissions.json', 'reddit/2017-12-06/politics_authors.json', 'reddit/2017-12-06/politics_comments.json', 'reddit/2017-12-06/politics_submissions.json', 'reddit/2017-12-06/soccer_authors.json', 'reddit/2017-12-06/soccer_comments.json', 'reddit/2017-12-06/soccer_submissions.json', 'reddit/2017-12-07/AskReddit_authors.json', 'reddit/2017-12-07/AskReddit_comments.json', 'reddit/2017-12-07/AskReddit_submissions.json', 'reddit/2017-12-07/Leagueoflegends_authors.json', 'reddit/2017-12-07/Leagueoflegends_comments.json', 'reddit/2017-12-07/Leagueoflegends_submissions.json', 'reddit/2017-12-07/politics_authors.json', 'reddit/2017-12-07/politics_comments.json', 'reddit/2017-12-07/politics_submissions.json', 'reddit/2017-12-07/soccer_authors.json', 'reddit/2017-12-07/soccer_comments.json', 'reddit/2017-12-07/soccer_submissions.json', 'reddit/2017-12-08/AskReddit_authors.json', 'reddit/2017-12-08/AskReddit_comments.json', 'reddit/2017-12-08/AskReddit_submissions.json', 'reddit/2017-12-08/Leagueoflegends_authors.json', 'reddit/2017-12-08/Leagueoflegends_comments.json', 'reddit/2017-12-08/Leagueoflegends_submissions.json', 'reddit/2017-12-08/politics_authors.json', 'reddit/2017-12-08/politics_comments.json', 'reddit/2017-12-08/politics_submissions.json', 'reddit/2017-12-08/soccer_authors.json', 'reddit/2017-12-08/soccer_comments.json', 'reddit/2017-12-08/soccer_submissions.json', 'reddit/2017-12-09/AskReddit_authors.json', 'reddit/2017-12-09/AskReddit_comments.json', 'reddit/2017-12-09/AskReddit_submissions.json', 'reddit/2017-12-09/Leagueoflegends_authors.json', 'reddit/2017-12-09/Leagueoflegends_comments.json', 'reddit/2017-12-09/Leagueoflegends_submissions.json', 'reddit/2017-12-09/politics_authors.json', 'reddit/2017-12-09/politics_comments.json', 'reddit/2017-12-09/politics_submissions.json', 'reddit/2017-12-09/soccer_authors.json', 'reddit/2017-12-09/soccer_comments.json', 'reddit/2017-12-09/soccer_submissions.json', 'reddit/2017-12-10/AskReddit_authors.json', 'reddit/2017-12-10/AskReddit_comments.json', 'reddit/2017-12-10/AskReddit_submissions.json', 'reddit/2017-12-10/Leagueoflegends_authors.json', 'reddit/2017-12-10/Leagueoflegends_comments.json', 'reddit/2017-12-10/Leagueoflegends_submissions.json', 'reddit/2017-12-10/politics_authors.json', 'reddit/2017-12-10/politics_comments.json', 'reddit/2017-12-10/politics_submissions.json', 'reddit/2017-12-10/soccer_authors.json', 'reddit/2017-12-10/soccer_comments.json', 'reddit/2017-12-10/soccer_submissions.json', 'reddit/2017-12-11/AskReddit_authors.json', 'reddit/2017-12-11/AskReddit_comments.json', 'reddit/2017-12-11/AskReddit_submissions.json', 'reddit/2017-12-11/Leagueoflegends_authors.json', 'reddit/2017-12-11/Leagueoflegends_comments.json', 'reddit/2017-12-11/Leagueoflegends_submissions.json', 'reddit/2017-12-11/politics_authors.json', 'reddit/2017-12-11/politics_comments.json', 'reddit/2017-12-11/politics_submissions.json', 'reddit/2017-12-11/soccer_authors.json', 'reddit/2017-12-11/soccer_comments.json', 'reddit/2017-12-11/soccer_submissions.json', 'reddit/2017-12-12/AskReddit_authors.json', 'reddit/2017-12-12/AskReddit_comments.json', 'reddit/2017-12-12/AskReddit_submissions.json', 'reddit/2017-12-12/Leagueoflegends_authors.json', 'reddit/2017-12-12/Leagueoflegends_comments.json', 'reddit/2017-12-12/Leagueoflegends_submissions.json', 'reddit/2017-12-12/politics_authors.json', 'reddit/2017-12-12/politics_comments.json', 'reddit/2017-12-12/politics_submissions.json', 'reddit/2017-12-12/soccer_authors.json', 'reddit/2017-12-12/soccer_comments.json', 'reddit/2017-12-12/soccer_submissions.json', 'reddit/2017-12-13/AskReddit_authors.json', 'reddit/2017-12-13/AskReddit_comments.json', 'reddit/2017-12-13/AskReddit_submissions.json', 'reddit/2017-12-13/Leagueoflegends_authors.json', 'reddit/2017-12-13/Leagueoflegends_comments.json', 'reddit/2017-12-13/Leagueoflegends_submissions.json', 'reddit/2017-12-13/politics_authors.json', 'reddit/2017-12-13/politics_comments.json', 'reddit/2017-12-13/politics_submissions.json', 'reddit/2017-12-13/soccer_authors.json', 'reddit/2017-12-13/soccer_comments.json', 'reddit/2017-12-13/soccer_submissions.json', 'reddit/2017-12-14/AskReddit_authors.json', 'reddit/2017-12-14/AskReddit_comments.json', 'reddit/2017-12-14/AskReddit_submissions.json', 'reddit/2017-12-14/Leagueoflegends_authors.json', 'reddit/2017-12-14/Leagueoflegends_comments.json', 'reddit/2017-12-14/Leagueoflegends_submissions.json', 'reddit/2017-12-14/politics_authors.json', 'reddit/2017-12-14/politics_comments.json', 'reddit/2017-12-14/politics_submissions.json', 'reddit/2017-12-14/soccer_authors.json', 'reddit/2017-12-14/soccer_comments.json', 'reddit/2017-12-14/soccer_submissions.json']

    # for obj in bucket_keys['Contents']:
    #     key = obj['Key']
    #     if key in ['reddit/AskReddit_subreddit.json', 'reddit/Leagueoflegends_subreddit.json',
    #                'reddit/politics_subreddit.json', 'reddit/soccer_subreddit.json']:
    #         continue
    #     keys.append(key)
    #
    # keys_to_data = {}
    # total_keys = len(keys)
    # for key in keys:
    #     print('Downloading key {}; keys left {}'.format(key, total_keys))
    #     data = s3.get_object(Bucket=bucket_name, Key=key)['Body']
    #     data = json.loads(data.read().decode('utf-8'))
    #     keys_to_data[key] = data
    #     with open('{}/{}'.format(BASE_DIR, key.replace('/', '_')), 'w') as output_file:
    #         json.dump(data, output_file)
    #     total_keys -= 1
    #
    # print('Finished writing all data to disk')

    # with open('/Users/lorenamesa/Workspace/georgetown_capstone/scrapers/reddit/all_subreddit_data.json') as output_file:
    #     keys_to_data = json.load(output_file)

    # 3. Insert subreddits into database

    for subreddit_name in SUBREDDITS:
        print('Inserting {}'.format(subreddit_name))
        subreddit = SubReddit({'name': subreddit_name})
        sql, cols = subreddit.to_insert_sql()

        try:
            q.cursor.execute(sql, cols)
        except IntegrityError as e:
            pass
        except Exception as e:
            print(e)
            print('Violating: {0}\n{1}'.format(sql, cols))
            pass

    # 4. If key not processed, insert all data into database
    finished_keys = []
    total_keys = len(keys)

    for key in keys:
        new_key = key[0:6] + '_' + key[7:17] + '_' + key[18:]

        with open('{}/{}'.format(BASE_DIR, new_key)) as output_file:
            key_data = json.load(output_file)

        print('Processing key {}'.format(key))
        if key in finished_keys:
            print('Processed {}, skipping'.format(key))
            continue
        for data in key_data:

            reddit_objs = []

            if 'authors' in key:
                reddit_objs.append(Author(data))

            if 'submissions' in key:
                reddit_objs.append(Author({'name': data.get('author')}))
                reddit_objs.append(Submission(data))

            if 'comments' in key:
                reddit_objs.append(Author({'name': data.get('author')}))
                reddit_objs.append(Comment(data))

            if key in finished_keys:
                print('Breaking out of processing {}, because already done'.format(key))
                total_keys -= 1
                print('Keys left: {}'.format(total_keys))
                break

            for reddit_obj in reddit_objs:
                if key in finished_keys:
                    print('Breaking out of processing {}, because already done'.format(key))
                    break
                sql, cols = reddit_obj.to_insert_sql()
                try:
                    q.cursor.execute(sql, cols)
                except IntegrityError as e:
                    print('Appending key b/c integrity error')
                    finished_keys.append(key)
                    pass
                except Exception as e:
                    print(e)
                    print('Violating: {0}\n{1}'.format(sql, cols))
                    pass

        print('Done processing key {}'.format(key))
        total_keys -= 1

        print('Keys left: {}'.format(total_keys))

        finished_keys.append(key)

        with open('{}_processed_keys.txt'.format(datetime.today().strftime('%Y-%m-%d')), 'w+') as output_file:
            output_file.write(key + '\n')




#     subreddit_submissions_to_data = dict.fromkeys(SUBREDDITS, {})
#
#
#     for table, sql in create_table_sql.items():
#         print('Check if table {0} exists'.format(table))
#         try:
#             q.cursor.execute('''
# SELECT EXISTS (
#    SELECT 1
#    FROM   information_schema.tables
#    WHERE  table_schema = 'public'
#    AND    table_name = '{}'
#    );
#    '''.format(table))
#             rows = q.cursor.fetchall()
#             print(rows)
#         except Exception as e:
#             print(e)
#