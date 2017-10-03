#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Example script that:
- Connects to an AWS database using: psycopg2
- Inserts a table into AWS database if table does not exist
- Writes data into the aforementioned table in AWS database
"""

from psycopg2._psycopg import InterfaceError

import yaml
import psycopg2
import os
import pandas as pd  # You can alias a library when imported
import csv
from datetime import datetime
from examples.useful_queries import QUERIES

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = yaml.load(open(PARENT_DIR + '/config.yml', 'r'))


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

    def execute(self, query, named_parameters=None, read=False):
        try:

            if named_parameters:
                self.cursor.execute(query, named_parameters)
            else:
                self.cursor.execute(query)

            if read:
                return self.cursor.fetchall()

        except InterfaceError as e:
            print('exception: {}'.format(e))

            self.__connect__()

            if named_parameters:
                self.cursor.execute(query, named_parameters)
            else:
                self.cursor.execute(query)

            if read:
                return self.cursor.fetchall()

        except Exception as e:
            raise Exception

class PandasQuery(Query):

    def execute(self, query):
        """

        :param query:
        :return:
        """
        key = query

        # TODO: Implement cache?
        value = None  # self.cache.get(key)

        if value is not None:
            return value
        # logger.info('Cache miss, getting query {} again'.format(query))

        try:
            value = pd.read_sql_query(query, self.cursor)
            # self.cache.add(key, value, CACHE_TIMEOUT)
            return value
        except:
            self.__connect__()
            value = pd.read_sql_query(query, self.cursor)
            # self.cache.add(key, value, CACHE_TIMEOUT)
            return value
        finally:
            self.connection.close()


def match_timestamp(timestamp_str):
    '''
    Notes on how to translate time:
    https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
    '''
    options = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S"
    ]

    for option in options:
        try:
            val = datetime.strptime(timestamp_str, option)
            return val
        except ValueError:
            continue
    raise Exception('Cannot match {}'.format(timestamp_str))

if __name__ == '__main__':
    q = Query(CONFIG['db'], False)

    result = q.execute(QUERIES['table_exist'], named_parameters=['public', 'wikipedia_talk_test'], read=True)

    if not result[0][0]:  # if not True (true meaning table exists)
        print('hai')
        q.execute('''
            CREATE TABLE wikipedia_talk_test (
                        rev_id INTEGER NOT NULL,
                        comment TEXT NOT NULL,
                        raw_comment TEXT NOT NULL,
                        timestamp TIMESTAMP NOT NULL,
                        page_id INTEGER NOT NULL,
                        page_title VARCHAR(250),
                        user_id INTEGER,
                        user_text TEXT,
                        bot BOOLEAN,
                        admin BOOLEAN
                );
        ''')

    pathway = PARENT_DIR + '/data/wikipedia-detox/comments_article_2015/'
    file_names = os.listdir(pathway)

    # Headers:
    # ['rev_id', 'comment', 'raw_comment', 'timestamp', 'page_id', 'page_title', 'user_id', 'user_text', 'bot', 'admin']
    # Example of timestamp: 2015-12-08T22:45:15Z

    with open(pathway + file_names[0]) as tsvfile:  # Only loading from first chunk_0.tsv file a 1,000 rows
        counter = 0
        tsvreader = csv.DictReader(tsvfile, delimiter="\t")
        for row in tsvreader:
            while counter < 1000:
                try:
                    #  Pass params to query - http://initd.org/psycopg/docs/usage.html#passing-parameters-to-sql-queries
                    q.execute(
                        """
                        INSERT INTO
                          wikipedia_talk_test(
                            rev_id, comment, raw_comment, timestamp, page_id, page_title, user_id,  user_text, bot,
                            admin
                          )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                        """,
                        [
                            row.get('rev_id'),
                            row.get('comment'),
                            row.get('raw_comment'),
                            match_timestamp(row.get('timestamp')),
                            row.get('page_id'),
                            row.get('page_title'),
                            int(float(row.get('user_id'))) if row.get('user_id') else -1,
                            row.get('user_text'),
                            bool(row.get('bot')),
                            bool(row.get('admin', False))
                        ]
                    )
                    print(counter)
                except Exception as e:
                    print(e)
                    break
                counter += 1

