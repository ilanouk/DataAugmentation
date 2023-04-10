from abc import ABC, abstractmethod
from pymongo import MongoClient


class DataBase(ABC):

    def __init__(self):

        self.client = MongoClient()

