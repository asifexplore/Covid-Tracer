from pymongo import MongoClient
from pprint import pprint


class MongoDBClient:
    '''Database Client to connect to MongoDB server.
    Args:
        uri (str): The uri for connection with mongo server. Must contain
        username and password.
        db_name (str): The which db you want to access in the database.
    '''

    def __init__(self, uri):
        self.uri = uri
        self.client = None
        self.db = None

    def connect_to_client(self):
        '''Connect to the server using crendentials inside uri.
        Returns:
            bool: a bool of whether connect is successful.
        '''
        try:
            self.client = MongoClient(self.uri)
            print('connected to mongo client')
            return True

        except Exception as e:
            print(e)
            return False

    def connect_to_database(self, db_name):
        '''Connect to db_name database using client.
        Returns:
            bool: a bool of whether connect is successful.
        '''
        try:
            self.db = self.client[db_name]
            print(f'connected to {db_name} db')
            return True

        except Exception as e:
            print(e)
            return False
