import shutil
import sys
import threading
import time
from datetime import datetime

from bson import ObjectId
from flask import *
import json
import os

from pymongo import collection
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from data_augmentation.augmentation import *
from database.DataBaseFile import *
from database.DataBaseUser import *
from flask_socketio import send, SocketIO, emit
import zipfile
import secrets
from flask_session import Session

import gevent, eventlet  # Important pour le serveur socket même si pas explicitement utilisé


app = Flask(__name__)
app.secret_key = secrets.token_hex(32) # La clé secrète est utilisée pour signer les données stockées dans la session,
                            # afin d'éviter que des utilisateurs ne puissent les falsifier.
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)

socketio = SocketIO(app)
uploadedFiles = []
uploadedFolders = []
app.template_folder = "templates/html/"
files = []
logs = {}

if not os.path.isdir("./uploads"):
    os.mkdir("./uploads")
if not os.path.isdir("./increased_data"):
    os.mkdir("./increased_data")
if os.path.exists("./forms/logs.json"):
    os.remove("./forms/logs.json")
if os.path.exists("./forms/form_signUp.json"):
    os.remove("./forms/form_signUp.json")


app.config['uploads'] = './uploads'
uploads = os.listdir(app.config['uploads'])

dataBaseUser = DataBaseUser("user")
dataBaseFile = DataBaseFile()

if os.path.exists(f"./uploads/.DS_Store"):
    os.remove(f"./uploads/.DS_Store")


@app.context_processor
def inject_os_functions():
    # créé un dictionnaire de fonctions à injecter
    fonctions = {}
    fonctions['isdir'] = os.path.isdir
    fonctions['normpath'] = os.path.normpath
    fonctions['getmtime'] = os.path.getmtime
    fonctions['strftime'] = datetime.strftime
    fonctions['fromtimestamp'] = datetime.fromtimestamp

    return fonctions


@app.route('/upload', methods=['GET', 'POST'])
def upload():

    if not 'user_id' in session:
        return redirect('/connexion')

    user_id = session["user_id"]
    uploadedFiles = dataBaseFile.getUploadedFiles(user_id)
    uploadedFolders = dataBaseFile.getUploadedFolders(user_id)

    if request.method == 'POST':
        # dataBaseFile.reset_DB()
        doublon = False
        file = request.files['file']
        folder = request.files['folder']
        if file.filename == '' and folder.filename == '':
            flash('No selected file')
            return render_template('uploadPage.html')

        pathUploadUser = f"{app.config['uploads']}/{session['user_id']}"
        if not os.path.isdir(pathUploadUser):
            os.mkdir(pathUploadUser)

        if file.filename != '':  # *************** FICHIER***************

            files = request.files.getlist('file')  # Liste de tous les fichiers de la requete recue
            for file in files:
                filename = secure_filename(file.filename)
                for fileU in uploadedFiles:
                    if fileU["name"] == filename:
                        doublon = True

                if not doublon:
                    uploadedFiles.append({"name": filename, "date": datetime.now()})
                    print("file : ", file)
                    path = os.path.join(app.config['uploads'], user_id, filename)
                    file.save(path)
                    file.filename = ''
                    flash('File successfully uploaded')
                    dataBaseFile.upload_file(path, user_id)  # On dépose le fichier dans la base de données

        if folder.filename != '':  # *********** DOSSIERS ************
            print("on passe la")
            folder = request.files.getlist('folder')  # Recuperation de la liste des dossiers
            folderName = folder[0].filename.rsplit('/', 1)[0]  # Supprimer l'extension de fichier
            folderName = secure_filename(folderName)
            print("folderName : ", folderName)
            folderPath = os.path.join(app.config['uploads'], user_id, folderName)  # Chemin du dossier à créer
            print("folderPath : ", folderPath)

            os.makedirs(folderPath, exist_ok=True)  # Créer le dossier s'il n'existe pas déjà

            for folderU in uploadedFolders:
                if folderU["name"] == folderName:
                    doublon = True

            if not doublon:
                uploadedFolders.append({"name": folderName, "date": datetime.now()})
                for file in folder:
                    fileName = secure_filename(file.filename.rsplit('/', 1)[-1])  # Nom du fichier
                    filePath = os.path.join(folderPath, fileName)  # Chemin du fichier à enregistrer
                    file.save(filePath)  # Enregistrer le fichier dans le dossier

            # Une fois que le dossier est créé, on dépose le dossier dans la base de données

            dataBaseFile.upload_file(folderPath, user_id, folder=True)

    return render_template('uploadPage.html', uploadedFiles=uploadedFiles, uploadedFolders=uploadedFolders)


@app.route('/uploads/view_file/<path:filename>')
def view_file(filename):
    return send_from_directory(app.config['uploads'], filename)


@app.route('/uploads/download_file/<path:filename>', methods=['GET', 'POST'])
def download_file(filename):
    user_id = session["user_id"]
    path = f"./uploads/{user_id}/{filename}"
    print("path  : ", path)
    return send_file(path, as_attachment=True)


@app.route('/uploads/download_folder/<path:foldername>')
def download_folder(foldername):
    user_id = session["user_id"]
    # Chemin absolu du dossier à compresser
    folderpath = os.path.join(app.config['uploads'], user_id, foldername)

    # Nom de l'archàive ZIP à créer
    zip_filename = foldername + '.zip'
    # Création de l'archive ZIP
    os.system(f"cd {os.path.dirname(folderpath)} && zip -r {zip_filename} {os.path.basename(folderpath)}")

    # ATTENTION : cette commande ne fonctionne que sur les systèmes UNIX , remplacer
    # par une commande équivalente sur les systèmes Windows ou utiliser la librairie zipfile

    # Envoi de l'archive ZIP en tant que fichier téléchargeable
    return send_file(os.path.join(os.path.dirname(folderpath), zip_filename), as_attachment=True)


@app.route('/home/download_data', methods=['GET', 'POST'])
def download_data():
    # Chemin absolu du dossier à compresser
    folderpath = "./data_augmentation/data"
    # Nom de l'archive ZIP à créer
    zip_filename = 'data.zip'
    # Création de l'archive ZIP avec la bibliothèque zipfile
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(folderpath):
            for file in files:
                zip_file.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), folderpath))

    # Envoi de l'archive ZIP en tant que fichier téléchargeable
    zip_file = send_file(os.path.join(os.getcwd(), zip_filename), as_attachment=True)
    deleteData()  # On supprime du cache les données qui ont étaient augmentées
    return zip_file


@app.route('/',methods = ['GET','POST'])
def index():
    if "delete_account" in request.form:

        user_id = ObjectId(session['user_id'])
        user_collection = dataBaseUser.collection_logs
        shutil.rmtree(f'./uploads/{user_id}')
        shutil.rmtree(f'./increased_data/{user_id}')

        db = dataBaseFile.client['uploads']
        db.drop_collection(user_collection)

        db = dataBaseFile.client['increased']
        db.drop_collection(user_collection)

        user_collection.delete_one({'_id' : user_id})

        print("\nl'utilisateur a bien été supprimé\n")
    return render_template('index.html')


@app.route('/inscription')
def inscription():
    return render_template('signUp.html')


@app.route('/connexion', defaults={'logout': 'False'})
@app.route('/connexion/<logout>')
def connexion(logout=False):

    if logout :
        # On supprime les logs
        session.pop('user_id', None)
        print("deconnexion")
        with open('./forms/logs.json', 'w') as f:
            json.dump({}, f)

    return render_template('login.html', error=False)



@app.route('/home/settings', methods=['GET', 'POST'])
def settings():
    if "mail" in request.form:

        user_data = {}
        for key in request.form:
            user_data[key] = request.form[key]  # Récuperer les données du formulaire sous forme de dictionnaire


        if dataBaseUser.mailExist(user_data['mail']):
            db_collection = dataBaseUser.collection_logs
            user_infos = db_collection.find_one({'email': user_data['mail']})
            user_id = ObjectId(user_infos['_id'])
            
            salt = user_infos['salt']
            newpass = user_data['newpass']
            newpassC = user_data['newpassconfirm']

            if (newpass == newpassC):  # s'il correspond à celui indiqué dans la BDD

                newpassword_hash = bcrypt.hashpw(newpass.encode('utf-8'), salt)  # chiffrement du mot de passe
                

                db_collection.find_one_and_update(  # on met à jour le mot de passe de l'utilisateur
                    {'_id': user_id},
                    {"$set":
                        {'password': newpassword_hash,
                        'passwordConfirm': newpassword_hash}
                    }, upsert=True
                )

                print("le mot de passe à été changé")
                return render_template('settings.html',result = "Votre mot de passe a été modifié")

            else:
                print("Le mot de passe saisi est incorrect, veuillez vérifier votre mot de passe.")
                return render_template('settings.html', passwordDifferent=True)  # sinon on retourne que le mot de passe indiqué est différent
            
        else:
            print("L'adresse mail saisie n'existe pas ou n'est pas utilisée")
            return render_template('settings.html', mailNotExists=True)  # sinon on retourne que le mail indiqué n'existe pas ou n'est pas utilisée

    return render_template('settings.html')




@app.route('/team')
def team():
    return render_template('team.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/documentation')
def documentation():
    return render_template('documentation.html')


@app.route('/home', methods=['GET', 'POST'])
def home():

    if 'user_id' in session:
        #return redirect('/connexion')
        print("user_id :", session['user_id'])
        user_id = session["user_id"]
        files_uploaded = dataBaseFile.getUploadedFiles(user_id)
        folders_uploaded = dataBaseFile.getUploadedFolders(user_id)
        uploads = files_uploaded + folders_uploaded
        files_increased = dataBaseFile.getIncreasedFiles(user_id)
        folders_increased = dataBaseFile.getIncreasedFolders(user_id)
        increased = files_increased + folders_increased

    if request.method == 'POST':

        # Si le form envoyé est celui du login car il y'a le name inputMail dans le form
        if "inputMail" in request.form:
            email = request.form['inputMail']
            password = request.form['inputPassword']

            if dataBaseUser.verif_user(email, password):

                collection = dataBaseUser.get_collection_logs()
                resultat = collection.find_one({'email': email})
                user_id = str(resultat['_id'])
                session['user_id'] = user_id
                logs = dict()
                # ajoute toutes les clefs valeurs de request.form dans le dictionnaire logs
                for key in request.form:
                    logs[key] = request.form[key]
                # ajoute le couple clef/valeur user_id au dictionnaire request.form
                logs["user_id"] = session["user_id"]
                # test si le fichier logs.json existe
                if not os.path.exists('./forms/logs.json'):
                    with open('./forms/logs.json', 'w') as f:
                        json.dump({}, f)

                with open('./forms/logs.json', 'w') as f:
                    json.dump(logs, f)

                # Si l'utilisateur est bien dans la base de données on renvoie la page d'accueil
                uploadedFiles = dataBaseFile.getUploadedFiles(user_id)
                uploadedFolders = dataBaseFile.getUploadedFolders(user_id)
                uploads = uploadedFiles + uploadedFolders
                files_increased = dataBaseFile.getIncreasedFiles(user_id)
                folders_increased = dataBaseFile.getIncreasedFolders(user_id)
                increased = files_increased + folders_increased
                return render_template('userPage.html', uploads=uploads, increased=increased)
            else:
                # Sinon on renvoie la page de connexion
                return render_template('login.html', error=True)

        # Sign Up

        if "firstName" in request.form:
            # stocker les données du formulaire dans un fichier json
            with open('./forms/form_signUp.json', 'w') as f:
                json.dump(request.form, f)
            # Récuperer les données du formulaire sous forme de dictionnaire
            with open("./forms/form_signUp.json") as f:
                user_data = json.load(f)
                
            if user_data['password'] != user_data['passwordConfirm']:
                # Si les mots de passe ne sont pas identiques on renvoie la page d'inscription
                return render_template('signUp.html', passwordDifferent=True)

            if dataBaseUser.add_user('./forms/form_signUp.json'):
                collection = dataBaseUser.get_collection_logs()
                resultat = collection.find_one({'email': user_data["email"]})
                user_id = str(resultat['_id'])
                session['user_id'] = user_id
                os.mkdir(f'./uploads/{user_id}')               # création des repertoires utilisateurs
                os.mkdir(f'./increased_data/{user_id}')
                uploadedFiles = dataBaseFile.getUploadedFiles(session['user_id'])
                uploadedFolders = dataBaseFile.getUploadedFolders(session['user_id'])
                uploads = uploadedFiles + uploadedFolders
                files_increased = dataBaseFile.getIncreasedFiles(session['user_id'])
                folders_increased = dataBaseFile.getIncreasedFolders(session['user_id'])
                increased = files_increased + folders_increased
                # Si l'utilisateur a bien été ajouté à la base de données on renvoie la page d'accueil
                return render_template('userPage.html', uploads=uploads, increased=increased)
            else:
                # Sinon on renvoie la page d'inscription
                return render_template('signUp.html', mailExisting=True)

    if 'user_id' in session:
        return render_template('userPage.html', uploads=uploads, increased=increased)
    else:
        return redirect('/connexion')


@app.route('/home/augmentation', methods=['GET', 'POST'])
def augmentation():
    user_id = session["user_id"]
    files_uploaded = dataBaseFile.getUploadedFiles(user_id)
    folders_uploaded = dataBaseFile.getUploadedFolders(user_id)
    uploads = files_uploaded + folders_uploaded

    if request.method == "POST":
        options = request.form.getlist('options')
        optionsValues = request.form.getlist('intensity')
        print(optionsValues)
        files_to_Augment = request.form.getlist("to_augment")
        print("Dossiers et/ou Fichiers choisis : ", files_to_Augment)
        for filename in files_to_Augment:
            augmentationFolder(filename, options, optionsValues)

        return Response("200", status=200)
    else:
        return render_template('userPage.html', uploads=uploads)


def augmentationFolder(path, options, optionsValues):
    # Chemin vers le dossier contenant les images à augmenter
    user_id = session["user_id"]
    input_folder = f"./uploads/{user_id}"
    output_folder = "./data_augmentation/data"
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    user_id = session["user_id"]

    nbFilesTraites = 0
    output_folder = output_folder + "/" + path
    print("output_folder : ", output_folder)
    if os.path.isdir(f"{input_folder}/{path}"):  # Directory
        if not os.path.isdir(output_folder):
            os.mkdir(output_folder)

        print("Passage dans directory")
        input_folder = f"./uploads/{user_id}/{path}"
        for filename in os.listdir(input_folder):  # Boucle à travers tous les fichiers du dossier
            nbFilesTraites += 1
            augmentationFile(filename, input_folder, output_folder, options, optionsValues)
            socketio.emit('updateProgressBar', {'progress': nbFilesTraites})
            socketio.sleep(0.00001)
            print(f"{input_folder}/{filename} traité")

        print("PathFolder : ", path)
        dataBaseFile.increased_file(path, user_id, folder=True)
    else:  # File
        output_folder = output_folder[:-4]
        if not os.path.isdir(output_folder):
            os.mkdir(output_folder)
        augmentationFile(path, input_folder, output_folder, options, optionsValues)
        nbFilesTraites += 1
        socketio.emit('updateProgressBar', {'progress': nbFilesTraites})
        socketio.sleep(0.00001)
        print(f"{input_folder}/{path} traité")
        print("PathFile : ", path)
        dataBaseFile.increased_file(path, user_id)


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            os.makedirs(d, exist_ok=True)
            copytree(s, d, symlinks, ignore)
        else:
            if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                shutil.copy2(s, d)


def deleteData():
    # Supprimer le dossier data augmentee
    if os.path.exists(f"./data.zip"):
        os.remove(f"./data.zip")
    user_id = session["user_id"]
    if os.path.exists("./data_augmentation/data"):
        print("./increased_data/" + user_id)
        copytree("./data_augmentation/data", "./increased_data/" + user_id)
        shutil.rmtree("./data_augmentation/data")

    print("Suppresion Effectuee")


@app.route('/uploads/delete_folder/<path:foldername>/<string:redirect_page>', methods=['GET', 'POST'])
@app.route('/uploads/delete_folder/<path:foldername>', defaults={'redirect_page': 'uploadPage.html'})
def delete_folder(foldername, redirect_page):
    user_id = session["user_id"]
    uploadedFiles = dataBaseFile.getUploadedFiles(user_id)
    uploadedFolders = dataBaseFile.getUploadedFolders(user_id)

    for folder in uploadedFolders:
        print("folder : ", folder)
        if foldername == folder["name"]:
            print("entreee")
            uploadedFolders.remove(folder)
            dataBaseFile.delete_upload_file(foldername, user_id, folder=True)
            # delete the folder
            shutil.rmtree(f"./uploads/{user_id}/{foldername}")

    if redirect_page == 'home':
        return redirect(url_for('home'))
    else:
        return render_template('uploadPage.html', uploadedFiles=uploadedFiles, uploadedFolders=uploadedFolders)


@app.route('/uploads/delete_file/<path:filename>/<string:redirect_page>', methods=['GET', 'POST'])
@app.route('/uploads/delete_file/<path:filename>', defaults={'redirect_page': 'uploadPage.html'})
def delete_file(filename, redirect_page):
    user_id = session["user_id"]
    uploadedFiles = dataBaseFile.getUploadedFiles(user_id)
    uploadedFolders = dataBaseFile.getUploadedFolders(user_id)

    for file in uploadedFiles:
        if filename == file["name"]:
            uploadedFiles.remove(file)
            dataBaseFile.delete_upload_file(filename, user_id)
            # delete from directory ./uploads
            os.remove(f"./uploads/{user_id}/{filename}")

    if redirect_page == 'home':
        return redirect(url_for('home'))
    else:
        return render_template('uploadPage.html', uploadedFiles=uploadedFiles, uploadedFolders=uploadedFolders)


# @app.route('/uploads/delete_increased_folder/<path:foldername>/<string:redirect_page>', methods=['GET', 'POST'])
@app.route('/uploads/delete_increased_folder/<path:foldername>')
def delete_increased_folder(foldername):
    user_id = session["user_id"]
    increasedFolders = dataBaseFile.getIncreasedFolders(user_id)

    for folder in increasedFolders:
        print("folder : ", folder)
        if foldername == folder["name"]:
            print("entreee")
            increasedFolders.remove(folder)
            dataBaseFile.delete_increased_file(foldername, user_id, folder=True)

            shutil.rmtree(f"./increased_data/{user_id }/{foldername}")

    # Actualiser la liste des fichiers et dossiers
    uploadedFiles = dataBaseFile.getUploadedFiles(user_id)
    uploadedFolders = dataBaseFile.getUploadedFolders(user_id)
    uploads = uploadedFiles + uploadedFolders
    files_increased = dataBaseFile.getIncreasedFiles(user_id)
    folders_increased = dataBaseFile.getIncreasedFolders(user_id)
    increased = files_increased + folders_increased

    return render_template('userPage.html', uploads=uploads, increased=increased)


# @app.route('/uploads/delete_increased_file/<path:filename>/<string:redirect_page>', methods=['GET', 'POST'])
@app.route('/uploads/delete_increased_file/<path:filename>')
def delete_increased_file(filename):
    print("on arv ici, on a le filename : ", filename)

    user_id = session["user_id"]
    increasedFiles = dataBaseFile.getIncreasedFiles(user_id)
    filenameWithoutExt = filename[:-4]
    print("increasedFiles : ", increasedFiles)
    for file in increasedFiles:
        if filename == file["name"]:
            dataBaseFile.delete_increased_file(filename, user_id)
            shutil.rmtree(f"./increased_data/{user_id }/{filenameWithoutExt}")

    uploadedFiles = dataBaseFile.getUploadedFiles(user_id)
    uploadedFolders = dataBaseFile.getUploadedFolders(user_id)
    uploads = uploadedFiles + uploadedFolders
    files_increased = dataBaseFile.getIncreasedFiles(user_id)
    folders_increased = dataBaseFile.getIncreasedFolders(user_id)
    increased = files_increased + folders_increased

    return render_template('userPage.html', uploads=uploads, increased=increased)


@app.route('/home/countFiles', methods=['POST', 'GET'])
def countFiles():
    foldername = request.form['foldername'].split("/")[-1]
    print("ici on a le foldername : ", foldername)
    count = 0
    user_id = session["user_id"]
    pathFolder = f"./uploads/{user_id}/{foldername}"

    print("foldername : ", pathFolder)
    for root, dirs, files in os.walk(f'{pathFolder}'):
        count += len(files)
    return str(count)


def getLogs():
    # get logs from form_login.json
    with open('./forms/logs.json', 'r') as f:
        logs = json.load(f)
    return logs


def get_folders(path):
    list_file = []
    for entry in os.scandir(path):
        list_file.append(entry.name)

    return list_file


@app.route('/gallery')
def gallery():
    user_id = session["user_id"]
    print("user_id : ", user_id)
    path_increased_data = './increased_data/' + user_id
    gallery = {}
    for entry in os.scandir(path_increased_data):
        if entry.name != ".DS_Store":
            path_increased_folder = path_increased_data + '/' + entry.name
            print("path_increased_folder : ", path_increased_folder)
            gallery[f'{entry.name}'] = get_folders(path_increased_folder)

    print("gallery : ", gallery)
    return render_template('imageGallery.html', content=gallery)


@app.route('/get_increased_image/<path:foldername>/<path:filename>')
def get_increased_image(foldername, filename):
    path = './increased_data/' + session["user_id"] + '/' + foldername + "/" + filename
    print("image_path : ", filename)
    return send_file(path, mimetype='image/jpeg')


def deleteIncreased():
    # Supprimer le dossier data augmentee
    if os.path.exists(f"./data_increased.zip"):
        os.remove(f"./data_increased.zip")

    print("Suppresion Effectuee")


@app.route('/home/download_increased/<path:foldername>', methods=['GET', 'POST'])
def download_increased(foldername):
    # Chemin absolu du dossier à compresser
    print("La on a le foldername : ", foldername)
    if foldername.endswith(".jpg") or foldername.endswith(".png") or foldername.endswith(".jpeg"):
        foldername = foldername[:-4]
    user_id = session["user_id"]
    folderpath = "./increased_data/" + user_id + "/" + foldername
    # Nom de l'archive ZIP à créer
    zip_filename = 'data_increased.zip'
    # Création de l'archive ZIP avec la bibliothèque zipfile
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk(folderpath):
            for file in files:
                zip_file.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), folderpath))

    # Envoi de l'archive ZIP en tant que fichier téléchargeable
    zip_file = send_file(os.path.join(os.getcwd(), zip_filename), as_attachment=True)
    deleteIncreased()  # On supprime du cache les données qui ont étaient augmentées
    return zip_file


@app.route('/home/personalSpace', methods=['POST', 'GET'])
def personalSpace():
    if request.method == 'POST':

        if "updateInfo" in request.form:

            user_data = {}
            for key in request.form:
                user_data[key] = request.form[key]  # Récuperer les données du formulaire sous forme de dictionnaire

            modif_info(user_data)


        elif "updatePass" in request.form:

            user_data = {}
            for key in request.form:
                user_data[key] = request.form[key]  # Récuperer les données du formulaire sous forme de dictionnaire

            modif_password(user_data)


    return render_template('personalSpace.html', infos=verif_infos())


def verif_infos():
    user_id = ObjectId(session["user_id"])
    db_collection = dataBaseUser.collection_logs
    user_infos = db_collection.find_one({'_id': user_id})
    return user_infos


def modif_password(user_data):
    user_id = ObjectId(session["user_id"])
    db_collection = dataBaseUser.collection_logs
    user_infos = db_collection.find_one({'_id': user_id})

    salt = user_infos['salt']
    password = user_data['password']  # le mot de passe courant de l'utilisateur
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)  # chiffrement

    if (password_hash == user_infos['password']):  # s'il correspond à celui indiqué dans la BDD

        newpassword = user_data['newpassword']  # alors on récupère le nouveau mot de passe de l'utilisateur
        newpassword_hash = bcrypt.hashpw(newpassword.encode('utf-8'), salt)  # chiffrement du mot de passe

        passwd_user = db_collection.find_one_and_update(  # on met à jour le mot de passe de l'utilisateur
            {'_id': user_id},
            {"$set":
                 {'password': newpassword_hash,
                  'passwordConfirm': newpassword_hash}
             }, upsert=True
        )

        print("le mot de passe à été changé")
        return render_template('personalSpace.html', infos=passwd_user)

    else:
        print("Le mot de passe saisi est incorrect, veuillez vérifier votre mot de passe.")
        return render_template('personalSpace.html', passwordDifferent=True, infos=verif_infos())  # sinon on retourne que le mot de passe indiqué est différent


def modif_info(user_data):
    prenom = user_data['firstName']
    nom = user_data['lastName']
    mail = user_data['email']
    sexe = user_data['gender']
    pays = user_data['country']

    user_id = ObjectId(session["user_id"])
    db_collection = dataBaseUser.collection_logs
    user_infos = db_collection.find_one({'_id': user_id})

    if not dataBaseUser.mailExist(mail) or (user_data["email"] == user_infos[
        "email"]):  # si l'adresse mail n'est pas utilisée ou si elle n'a pas été modifiée

        modif_user = db_collection.find_one_and_update(
            {'_id': user_id},
            {"$set":
                 {'firstName': prenom,
                  'lastName': nom,
                  'email': mail,
                  'country': pays,
                  'gender': sexe}
             }, upsert=True
        )

        print("les informations de l'utilisateur ont bien été mises à jour")
        return render_template('personalSpace.html', infos=modif_user)

    else:
        modif_user = db_collection.find_one_and_update(
            {'_id': user_id},
            {"$set":
                 {'firstName': prenom,
                  'lastName': nom,
                  'country': pays,
                  'gender': sexe}
             }, upsert=True
        )

        print("L'adresse mail a déjà été utilisée par sur un compte")
        return render_template('personalSpace.html', infos=modif_user, mailExisting=True)



if __name__ == '__main__':
    socketio.run(port=8080, debug=True, app=app)
    # app.run(debug=True, port=8080)
