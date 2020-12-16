from pymongo import MongoClient
from sqlalchemy import create_engine


class MongoConnection(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connection = None

    def __enter__(self):
        self.connection = MongoClient(self.host, self.port)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()


class SqlConnection(object):
    def __init__(self, uri):
        self.connection = create_engine(uri).connect()
