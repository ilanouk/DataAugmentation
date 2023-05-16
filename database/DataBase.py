from abc import ABC, abstractmethod
from pymongo import MongoClient
from bson import ObjectId


class DataBase(ABC):
    """
    Classe qui permet la connexion à la base de donnée

    """

    def __init__(self):
        """
        Instancier la connexion à la base de donnée
        :param None
        :return None

        """

        self.client = MongoClient()

