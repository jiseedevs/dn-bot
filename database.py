'''
    This module is responsible for performing queries to the database via
    database API
'''
import os
import datetime

import psycopg2

from dotenv import load_dotenv

load_dotenv('./env.db')

class DatabaseHandler:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseHandler, cls).__new__(cls)

        return cls._instance

    def start(self):
        '''
            Connects to the database.
        '''
        self.connection = psycopg2.connect(
            os.getenv('DBNAME')
            )
        self.cursor = self.connection.cursor()

    def stop(self):
        '''
            Close the database connection.
        '''
        self.connection.close()

    def create_table(self):

        if self.cursor:
            self.cursor.execute(
                '''
                    CREATE TABLE IF NOT EXISTS webpage
                    (
                        id SERIAL PRIMARY KEY,
                        username TEXT NOT NULL,
                        url TEXT NOT NULL,
                        target TEXT,
                        html TEXT NOT NULL,
                        encrypted TEXT NOT NULL,
                        date_added timestamp DEFAULT (%s)
                    )
                ''', (datetime.datetime.now(),)
            )

            self.connection.commit()

    def _test_insert(self):
        '''
            Used to test inserts after creation of table.
        '''
        if self.cursor:
            self.cursor.execute(
                '''
                    INSERT INTO webpage (username, url, target, html, encrypted) VALUES (%s, %s, %s, %s, %s)
                ''', ('jiseoh', 'https://www.sea.dragonnest.com/news/notice', [], 'sample html', 'sample encrypted')
            )

            self.connection.commit()

    def check_if_table_exists(self, table):
        pass

    def insert_to_webpage(self, data):
        '''
            Save record to the table.
        '''
        if isinstance(data, dict):

            if self.cursor:
                self.cursor.execute(
                    '''
                        INSERT INTO webpage (username, url, target, html, encrypted) VALUES (%(username)s, %(url)s, %(target)s, %(html)s, %(encrypted)s)
                    ''',
                    (
                        data
                    )
                    )
                self.connection.commit()

    def get_user_records(self, data):
        '''
            Get records to specific user if url is specified, return the record otherwise return all records of the user.
            data: must be a dictionary containing;
              - username
              - url

        '''

        if self.cursor and data:

            if data.get('url') is None:
                query = self.cursor.execute(
                   '''
                        SELECT * FROM webpage where username=%(username)s;
                    ''', data
                )
            else:
                query = self.cursor.execute(
                    '''
                        SELECT * FROM webpage WHERE username=%(username)s AND url=%(url)s;
                    ''', data
                )

            self.connection.commit()
            return self.cursor.fetchall()

        return None

    def get_all_url(self):
        if self.cursor:
            self.cursor.execute(
                    '''
                        SELECT * FROM webpage;
                    '''
                    )
            self.connection.commit()
            return self.cursor.fetchall()

    def update_record(self, data):
        '''
            Updates the record base on user and url given.
        '''

        if self.cursor and data is not None:
            self.cursor.execute(
                '''
                    UPDATE webpage SET html=%(html)s, encrypted=%(encrypted)s WHERE username=%(username)s and url=%(url)s;
                ''', data
            )
            self.connection.commit()
