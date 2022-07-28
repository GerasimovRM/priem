from pymongo import MongoClient

from common import Singleton
from config import MONGODB_URL


class DbClient(MongoClient, metaclass=Singleton):
    def __init__(self):
        super().__init__(MONGODB_URL)
