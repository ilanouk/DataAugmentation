import json

import os
from abc import ABC
from bson import ObjectId
from pymongo import MongoClient
import gridfs
import bcrypt

from database.DataBase import DataBase


class DataBaseUser(DataBase):
    """
    Classe qui gère les utilisateurs et leurs infos dans la base de données
    """

    def __init__(self, db_name):
        """
        Constructeur de la classe DataBaseUser

        :param db_name: nom de la base de donnée
        :type db_name: str

        """
        super().__init__()
        self.db_names = self.client.list_database_names()
        if "user" not in self.db_names:
            self.client["user"].create_collection("files")
        self.db = self.client[db_name]
        self.collection_logs = self.db["logs"]

        if "logs" not in self.db.list_collection_names():
            self.db.create_collection("logs")

    def add_user(self, json_logs):
        """
        Méthode permettant d'ajouter un utilisateur et ses informations dans la base de données

        :param json_logs: fichier json qui contient ses informations
        :type json_logs: str
        :return: l'ID de l'utilisateur nouvellement crée qui est un objet bson.objectid.ObjectId
        :rtype: bson.objectid.ObjectId

        """
        # json_logs est le chemin vers le fichier JSON contenant les informations de l'utilisateur
        # Chargement du fichier JSON
        with open(json_logs) as f:
            user_data = json.load(f)

        # Tester si l'email entré n'est pas déjà utilisé
        if self.collection_logs.find_one({"email": user_data["email"]}):  # si l'email existe déjà
            print("L'adresse e-mail est déjà utilisée")
            return False
        else:
            salt = bcrypt.gensalt(rounds=12)
            user_data["password"] = bcrypt.hashpw(user_data["password"].encode('utf-8'), salt)
            user_data["passwordConfirm"] = user_data["password"]
            user_data["salt"] = salt  # stockage du salt pour la vérification du mot de passe
            # Insertion de l'utilisateur dans la base de donnée
            result = self.collection_logs.insert_one(user_data)
            # Récupération de l'ID de l'utilisateur nouvellement créé
            user_ID = result.inserted_id
            print(f"Utilisateur créé avec l'ID : {user_ID}")

            # Création de sa collection dans increased et uploads
            db_uploads = self.client["uploads"]

            db_increased = self.client["increased"]

            db_uploads.create_collection(str(user_ID))
            db_increased.create_collection(str(user_ID))

            return user_ID

    def afficher_utilisateurs(self):
        """
        Affiche sur la console les utilisateurs présents dans la base de donnée

        """
        # Récupération de tous les documents de la collection
        utilisateurs = self.collection_logs.find()
        # Affichage des informations pour chaque utilisateur
        for utilisateur in utilisateurs:
            print(f"Nom : {utilisateur['lastName']}")
            print(f"Adresse e-mail : {utilisateur['email']}")
            print(f"Mot de passe : {utilisateur['password']}")
            print(f"Salt : {utilisateur['salt']}")
            print("------------------------------")

    def verif_user(self, email, password):
        """
        Vérifie les informations d'identification de l'utilisateur

        :param email: l'email de l'utilisateur
        :type email: str
        :param password: le mot de passe de l'utilisateur
        :type password: str
        :return: Retourne False si la vérification a échoué
        :rtype: bool

        """
        utilisateur = self.collection_logs.find_one({'email': email})
        if utilisateur:
            # vérifier si le mot de passe entré correspond au mot de passe stocké pour l'utilisateur
            salt = utilisateur['salt']
            password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
            if password_hash == utilisateur['password']:
                print("L'utilisateur est authentifié")
                if not os.path.exists(f"./uploads/{utilisateur['_id']}"):
                    os.makedirs(f"./uploads/{utilisateur['_id']}")
                if not os.path.exists(f"./increased_data/{utilisateur['_id']}"):
                    os.makedirs(f"./increased_data/{utilisateur['_id']}")
                return True
            print("L'adresse Mail ou le mot de passe est incorrect")
        return False

    def mailExist(self, mail):
        """
        Vérifie si un mail est déjà présent dans la base de donnée ou non

        :param mail: l'email de l'utilisateur
        :type mail: str
        :return: Retourne True si l'email existe déjà False sinon
        :rtype: bool

        """
        if self.collection_logs.find_one({"email": mail}):  # si l'email existe déjà
            print("L'adresse e-mail est déjà utilisée")
            return True
        else:
            return False

    def getSalt(self, email):
        """
        Récupère le "Salt" qui est une valeur aléatoire unique utilisée en cryptographie

        :param email: l'email de l'utilisateur
        :type email: str
        :return: Renvoie le "Salt" de l'utilisateur si celui-ci est présent dans la base de données
        :rtype: Union[str,None]

        """
        utilisateur = self.collection_logs.find_one({'email': email})
        if utilisateur:
            return utilisateur['salt']
        return None

    def get_collection_logs(self):
        """
        Renvoie la collection "logs" qui comporte les informations sur les utilisateurs

        :return: un objet pymongo.collection.Collection représentant la collection "logs"
        :rtype: pymongo.collection.Collection

        """
        return self.collection_logs
