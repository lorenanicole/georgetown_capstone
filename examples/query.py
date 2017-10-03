from psycopg2._psycopg import InterfaceError

import os
import pandas as pd
import psycopg2
import yaml

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
