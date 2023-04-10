import json
import os
from abc import ABC

from pymongo import MongoClient
import gridfs
import bcrypt

from database.DataBase import DataBase


class DataBaseUser(DataBase):

    def __init__(self,db_name):
        super().__init__()
        self.db_names = self.client.list_database_names()
        if "user" not in self.db_names:
            self.client["user"].create_collection("files")
        self.db = self.client[db_name]
        self.collection_logs = self.db["logs"]

        if "logs" not in self.db.list_collection_names():
            self.db.create_collection("logs")


    def add_user(self, json_logs):
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
        # Récupération de tous les documents de la collection
        utilisateurs = self.collection_logs.find()
        # Affichage des informations pour chaque utilisateur
        for utilisateur in utilisateurs:
            print(f"Nom : {utilisateur['lastName']}")
            print(f"Adresse e-mail : {utilisateur['email']}")
            print(f"Mot de passe : {utilisateur['password']}")
            print(f"Salt : {utilisateur['salt']}")
            print("------------------------------")

    # vérifier les informations d'identification de l'utilisateur
    def verif_user(self, email, password):

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
        if self.collection_logs.find_one({"email": mail}):  # si l'email existe déjà
            print("L'adresse e-mail est déjà utilisée")
            return True
        else:
            return False


    def getSalt(self,email):
        utilisateur = self.collection_logs.find_one({'email': email})
        if utilisateur:
            return utilisateur['salt']
        return None

    def get_collection_logs(self):
        return self.collection_logs

