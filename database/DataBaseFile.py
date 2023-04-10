import json
import os
from abc import ABC
from datetime import datetime
from dateutil.parser import parse

from pymongo import MongoClient
import gridfs
import bcrypt

from database.DataBase import DataBase


class DataBaseFile(DataBase):

    def __init__(self):
        super().__init__()
        self.db_names = self.client.list_database_names()
        if "uploads" not in self.db_names:
            self.client["uploads"].create_collection("files")
        if "increased" not in self.db_names:
            self.client["increased"].create_collection("files")
        self.db_uploads = self.client["uploads"]
        self.db_increased = self.client["increased"]

    def upload_file(self, path, userID, folder=False):

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

    def increased_file(self, path, userID, folder=False):

        user_collection = self.db_increased[userID]
        # print everything in the collection

        filename = path
        path = "./increased_data/" + userID + "/" + path
        os.makedirs("./increased_data/" + userID, exist_ok=True)
        # Insérer un fichier dans la collection
        if folder:
            folder = {"foldername": filename, "path": path, "date": datetime.now()}
            user_collection.insert_one(folder)
        else:
            path = path[:-4]
            file = {"filename": filename, "path": path, "date": datetime.now()}
            user_collection.insert_one(file)

    def delete_upload_file(self, filename, user_id, folder=False):
        if folder:
            print("Suppression du dossier : ", filename, " de la base de données")
            user_collection = self.db_uploads[user_id]
            user_collection.delete_one({"foldername": filename})

        else:
            print("Suppression du fichier : ", filename, " de la base de données")
            user_collection = self.db_uploads[user_id]
            user_collection.delete_one({"filename": filename})

    def delete_increased_file(self, filename, user_id, folder=False):

        if folder:
            print("Suppression du dossier : ", filename, " de la base de données")
            user_collection = self.db_increased[user_id]
            user_collection.delete_one({"foldername": filename})

        else:
            print("Suppression du fichier : ", filename, " de la base de données")
            user_collection = self.db_increased[user_id]
            user_collection.delete_one({"filename": filename})

    def reset_DB(self):
        self.collection_Uploads.files.drop()
        self.collection_Uploads.chunks.drop()
        # supprimer tous les fichiers de la base de données

    def getUploadedFiles(self, user_id):
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
        increase = self.db_increased[user_id]
        increased_folders = []
        for folder_obj in increase.find():
            if 'foldername' in folder_obj:
                folder_data = {}
                folder_data["name"] = folder_obj['foldername']
                folder_data["date"] = folder_obj['date']
                increased_folders.append(folder_data)
        return increased_folders


