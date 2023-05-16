import json

import os
from abc import ABC
from datetime import datetime
from dateutil.parser import parse
from bson import ObjectId
from pymongo import MongoClient
import gridfs
import bcrypt

from database.DataBase import DataBase


class DataBaseFile(DataBase):
    """
    Classe qui gère la collection dédier aux fichiers

    """

    def __init__(self):
        """
        Constructeur qui crée un objet DataBaseFile, crée les collections "uploads" et "increased"

        """
        super().__init__()
        self.db_names = self.client.list_database_names()
        if "uploads" not in self.db_names:
            self.client["uploads"].create_collection("files")
        if "increased" not in self.db_names:
            self.client["increased"].create_collection("files")
        self.db_uploads = self.client["uploads"]
        self.db_increased = self.client["increased"]

    def upload_file(self, path, userID, folder=False):
        """
        Méthode permettant d'insérer un fichier/dossier uploadé par l'utilisateur vers la base de données

        :param path: le chemin complet menant au fichier
        :type path: str
        :param userID: l'ID de l'utilisateur
        :type userID: str
        :param folder: Vérifie s'il s'agit d'un dossier ou d'un fichier
        :type folder: bool


        """

        user_collection = self.db_uploads[userID]
        filename = path.rsplit("/", 1)[1]
        path = f"uploads/{userID}/{filename}"

        # Insérer un fichier dans la collection
        if folder:
            folder = {"foldername": filename, "path": path, "date": datetime.now()}
            user_collection.insert_one(folder)
        else:
            file = {"filename": filename, "path": path, "date": datetime.now()}
            user_collection.insert_one(file)

    def increased_file(self, path, userID):
        """
        Méthode permettant d'insérer un fichier/dossier après augmentation dans la base de données

        :param path: le chemin complet menant au fichier
        :type path: str
        :param userID: l'ID de l'utilisateur
        :type userID: str


        """
        user_collection = self.db_increased[userID]
        # print everything in the collection

        filename = path.rsplit("/",1)[1]
        file_path = path.rsplit("/",1)[0]
        foldername = file_path.rsplit("/",1)[1]



        os.makedirs("./increased_data/" + userID, exist_ok=True)
        # Insérer un fichier dans la collection
        folder = {"foldername": foldername, "path": file_path, "date": datetime.now()}
        user_collection.insert_one(folder)

    def delete_upload_file(self, filename, user_id, folder=False):
        """
        Supprime un fichier/dossier uploadé par l'utilisateur dans la base de données

        :param filename: le fichier ciblé
        :type filename: str
        :param userID: l'ID de l'utilisateur
        :type userID: str
        :param folder: Vérifie s'il s'agit d'un dossier ou d'un fichier
        :type folder: bool


        """
        if folder:
            print("Suppression du dossier : ", filename, " de la base de données")
            user_collection = self.db_uploads[user_id]
            user_collection.delete_one({"foldername": filename})

        else:
            print("Suppression du fichier : ", filename, " de la base de données")
            user_collection = self.db_uploads[user_id]
            user_collection.delete_one({"filename": filename})

    def delete_increased_file(self, filename, user_id):
        """
        Supprime un fichier/dossier augmenté dans la base de données

        :param filename: le fichier ciblé
        :type filename: str
        :param userID: l'ID de l'utilisateur
        :type userID: str

        """

        print("Suppression du dossier : ", filename, " de la base de données")
        user_collection = self.db_increased[user_id]
        user_collection.delete_one({"foldername": filename})

    def reset_DB(self):
        """
        Supprime tous les fichiers de la base de données

        """
        self.collection_Uploads.files.drop()
        self.collection_Uploads.chunks.drop()


    def getUploadedFiles(self, user_id):
        """
        Récupérer tous les fichiers uploadés par l'utilisateur spécifié

        :param user_id: l'ID de l'utilisateur
        :type user_id: str
        :return: Tous les fichiers uploadés appartenant à l'utilisateur ID (liste de dictionnaire)
        :rtype: list

        """
        uploads = self.db_uploads[user_id]
        uploaded_files = []
        for file_obj in uploads.find():
            if 'filename' in file_obj:
                file_data = {}
                file_data["name"] = file_obj['filename']
                file_data["date"] = file_obj['date']
                uploaded_files.append(file_data)
                print(file_data)
        return uploaded_files

    def getUploadedFolders(self, user_id):
        """
        Récupérer tous les dossiers uploadés par l'utilisateur spécifié

        :param user_id: l'ID de l'utilisateur
        :type user_id: str
        :return: Tous les dossiers uploadés appartenant à l'utilisateur ID
        :rtype: list

        """
        uploads = self.db_uploads[user_id]
        uploaded_folders = []
        for folder_obj in uploads.find():
            if 'foldername' in folder_obj:
                folder_data = {}
                folder_data["name"] = folder_obj['foldername']
                folder_data["date"] = folder_obj['date']
                uploaded_folders.append(folder_data)
        return uploaded_folders

    def getIncreasedFiles(self, user_id):
        """
        Récupérer tous les fichiers augmentés par l'utilisateur spécifié

        :param user_id: l'ID de l'utilisateur
        :type user_id: str
        :return: Tous les fichiers augmentés appartenant à l'utilisateur ID
        :rtype: list

        """
        increase = self.db_increased[user_id]
        increased_files = []
        for file_obj in increase.find():
            if 'filename' in file_obj:
                file_data = {}
                file_data["name"] = file_obj['filename']
                file_data["date"] = file_obj['date']
                increased_files.append(file_data)
        return increased_files

    def getIncreasedFolders(self, user_id):
        """
        Récupérer tous les dossiers augmentés par l'utilisateur spécifié

        :param user_id: l'ID de l'utilisateur
        :type user_id: str
        :return: Tous les dossiers augmentés appartenant à l'utilisateur ID
        :rtype: list

        """
        increase = self.db_increased[user_id]
        increased_folders = []
        for folder_obj in increase.find():
            if 'foldername' in folder_obj:
                folder_data = {}
                folder_data["name"] = folder_obj['foldername']
                folder_data["date"] = folder_obj['date']
                increased_folders.append(folder_data)
        return increased_folders


