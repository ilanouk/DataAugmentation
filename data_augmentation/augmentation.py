import sys

import cv2
import shutil
import os
from .traitementIntensite import *


def augmentationFile(filename, input_folder, output_folder, options, optionsValues):
    """
    La fonction effectue des opérations de transformation sur une image en fonction des options sélectionnées par l'utilisateur et des intensités correspondantes.
    Pour chaque option, la fonction vérifie si elle est présente dans la liste des options.
    Si c'est le cas et que l'intensité correspondante est supérieure à zéro,
    la fonction effectue la transformation et sauvegarde l'image transformée dans le dossier de sortie.
    Si l'intensité est nulle, la fonction passe simplement à l'option suivante.

    :param filename: le nom du fichier image à traiter.
    :type filename: str
    :param input_folder: le dossier où le fichier image est stocké.
    :type input_folder: str
    :param output_folder: le dossier où les images augmentés seront stockées.
    :type output_folder: str
    :param options: les options de transformation à appliquer à l'image.
    :type options: list
    :param optionsValues: l'intensité des transformations sélectionnées par l'utilisateur pour chaque option.
    :type optionsValues: list


    """
    optionsValues = [int(x) for x in optionsValues]
    i = 0
    # afficher le chemin du répertoire actuel
    print("Le répertoire de travail actuel est : ", os.getcwd())

    # Vérifier si le fichier est une image
    if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png") or filename.endswith(".gif"):
        # Charger l'image avec OpenCV
        image = cv2.imread(os.path.join(input_folder, filename))
        if "rotation" in options:

            # Effectuer la rotation de l'image de 90 degrés
            if optionsValues[i] > 0 :
                rotated_image = rotation(image, 90, intensity=optionsValues[i])
                save_img(rotated_image, filename, "_rotated.jpg", output_folder)
                save_img(rotated_image, filename, "_rotated.jpg", "./data_augmentation/data")
                i = i + 1
            else : #dans le cas où il a été coché mais mis a 0% faut augmenter pour s'adapter aux indices de optionsValues
                i = i + 1

        if "zoom" in options:

            # Appliquer le zoom sur l'image
            if optionsValues[i] > 0 :
                zoomed_image = zoom(image, 4, intensity=optionsValues[i])
                save_img(zoomed_image, filename, "_zoomed.jpg", output_folder)
                save_img(zoomed_image, filename, "_zoomed.jpg", "./data_augmentation/data")
                i = i + 1
            else : #dans le cas où il a été coché mais mis a 0% faut augmenter pour s'adapter aux indices de optionsValues
                i = i + 1

        if "translation" in options:

            # Translation de l'image
            if optionsValues[i] > 0 :
                translated_image = translate(image, 300, 300, intensity=optionsValues[i])
                save_img(translated_image, filename, "_translated.jpg", output_folder)
                save_img(translated_image, filename, "_translated.jpg", "./data_augmentation/data")
                i = i + 1
            else : #dans le cas où il a été coché mais mis a 0% faut augmenter pour s'adapter aux indices de optionsValues
                i = i + 1

        if "flippedX" in options:
            # retournement de l'image en horizontal
            flippedX_image = mirror(image, 1)
            save_img(flippedX_image, filename, "_flippedX.jpg", output_folder)
            save_img(flippedX_image, filename, "_flippedX.jpg", "./data_augmentation/data")

        if "flippedY" in options:
            # retournement de l'image en vertical
            flippedY_image = mirror(image, 0)
            save_img(flippedY_image, filename, "_flippedY.jpg", output_folder)
            save_img(flippedY_image, filename, "_flippedY.jpg", "./data_augmentation/data")

        if "noise" in options:

            # Ajout de bruit gaussien
            if optionsValues[i] > 0 :
                noise_image = add_gaussian_noise(image, 0, 40, intensity=optionsValues[i])
                save_img(noise_image, filename, "_noise.jpg", output_folder)
                save_img(noise_image, filename, "_noise.jpg", "./data_augmentation/data")
                i = i + 1
            else : #dans le cas où il a été coché mais mis a 0% faut augmenter pour s'adapter aux indices de optionsValues
                i = i + 1

        if "blur" in options:

            # Ajout de flou gaussien
            if optionsValues[i] > 0 :
                blur_image = blur(image, 21, 10, intensity=optionsValues[i])
                save_img(blur_image, filename, "_blur.jpg", output_folder)
                save_img(blur_image, filename, "_blur.jpg", "./data_augmentation/data")
                i = i + 1
            else : #dans le cas où il a été coché mais mis a 0% faut augmenter pour s'adapter aux indices de optionsValues
                i = i + 1

        if "distortion" in options:

            # Distorsion de l'image
            if optionsValues[i] > 0 :
                distorded_image = distortion(image,intensity=optionsValues[i])
                save_img(distorded_image, filename, "_distorded.jpg", output_folder)
                save_img(distorded_image, filename, "_distorded.jpg", "./data_augmentation/data")
                i = i + 1
            else : #dans le cas où il a été coché mais mis a 0% faut augmenter pour s'adapter aux indices de optionsValues
                i = i + 1

        if "brightness" in options:

            # Modifier la luminosité de l'image, image plus lumineuse
            if optionsValues[i] > 0 :
                brightness_image = luminosity(image, beta=50, intensity=optionsValues[i])
                save_img(brightness_image, filename, "_brightness.jpg", output_folder)
                save_img(brightness_image, filename, "_brightness.jpg", "./data_augmentation/data")
                i = i + 1
            else : #dans le cas où il a été coché mais mis a 0% faut augmenter pour s'adapter aux indices de optionsValues
                i = i + 1

        if "contrast" in options:

            # Avec du contraste
            if optionsValues[i] > 0 :
                contrast_image = contrast(image, alpha=3, intensity=optionsValues[i])
                save_img(contrast_image, filename, "_contrast.jpg", output_folder)
                save_img(contrast_image, filename, "_contrast.jpg", "./data_augmentation/data")
                i = i + 1
            else : #dans le cas où il a été coché mais mis a 0% faut augmenter pour s'adapter aux indices de optionsValues
                i = i + 1

        if "darkness" in options:

            # Avec du contraste et sombre
            if optionsValues[i] > 0 :
                darker_contrast_image = darkness(image, intensity=optionsValues[i])
                save_img(darker_contrast_image, filename, "_darker.jpg", output_folder)
                save_img(darker_contrast_image, filename, "_darker.jpg", "./data_augmentation/data")
                i = i + 1
            else : #dans le cas où il a été coché mais mis a 0% faut augmenter pour s'adapter aux indices de optionsValues
                i = i + 1