import sys

import cv2
import shutil
import os
from .traitementIntensite import *


def augmentationFile(filename, input_folder, output_folder, options, optionsValues):
    #FAUX : optionsValues est renvoyé même si la case a été désélectionné (value = 50% dans userpage) longueur ==9 toujours
    #optionsValues renvoie que ceux qui ont été sélectionné
    optionsValues = [int(x) for x in optionsValues]
    i = 0

    # Vérifier si le fichier est une image
    if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png") or filename.endswith(".gif"):
        # Charger l'image avec OpenCV
        image = cv2.imread(os.path.join(input_folder, filename))
        print(optionsValues)
        if "rotation" in options:

            # Effectuer la rotation de l'image de 90 degrés
            if optionsValues[i] > 0 :
                print("DANS ROTATION"+ str(i))
                rotated_image = rotation(image, 90, intensity=optionsValues[i])
                save_img(rotated_image, filename, "_rotated.jpg", output_folder)
                i = i + 1
            else : #dans le cas où il a été coché mais mis a 0% faut augmenter pour s'adapter aux indices de optionsValues
                i = i + 1

        if "zoom" in options:

            # Appliquer le zoom sur l'image
            if optionsValues[i] > 0 :
                print("DANS ZOOM : "+str(i))
                zoomed_image = zoom(image, 4, intensity=optionsValues[i])
                save_img(zoomed_image, filename, "_zoomed.jpg", output_folder)
                i = i + 1
            else : #dans le cas où il a été coché mais mis a 0% faut augmenter pour s'adapter aux indices de optionsValues
                i = i + 1

        if "translation" in options:

            # Translation de l'image
            if optionsValues[i] > 0 :
                print("DANS TRANSLAT : "+str(i))
                translated_image = translate(image, 300, 300, intensity=optionsValues[i])
                save_img(translated_image, filename, "_translated.jpg", output_folder)
                i = i + 1
            else : #dans le cas où il a été coché mais mis a 0% faut augmenter pour s'adapter aux indices de optionsValues
                i = i + 1

        if "flippedX" in options:
            print("DANS FLIPPEDX")
            # retournement de l'image en horizontal
            flippedX_image = mirror(image, 1)
            save_img(flippedX_image, filename, "_flippedX.jpg", output_folder)

        if "flippedY" in options:
            print("DANS FLIPPEDY")
            # retournement de l'image en vertical
            flippedY_image = mirror(image, 0)
            save_img(flippedY_image, filename, "_flippedY.jpg", output_folder)

        if "noise" in options:

            # Ajout de bruit gaussien
            if optionsValues[i] > 0 :
                print("DANS NOISE : "+str(i))
                noise_image = add_gaussian_noise(image, 0, 40, intensity=optionsValues[i])
                save_img(noise_image, filename, "_noise.jpg", output_folder)
                i = i + 1
            else : #dans le cas où il a été coché mais mis a 0% faut augmenter pour s'adapter aux indices de optionsValues
                i = i + 1

        if "blur" in options:

            # Ajout de flou gaussien
            if optionsValues[i] > 0 :
                print("DANS BLUR : "+str(i))
                blur_image = blur(image, 21, 10, intensity=optionsValues[i])
                save_img(blur_image, filename, "_blur.jpg", output_folder)
                i = i + 1
            else : #dans le cas où il a été coché mais mis a 0% faut augmenter pour s'adapter aux indices de optionsValues
                i = i + 1

        if "distortion" in options:

            # Distorsion de l'image
            if optionsValues[i] > 0 :
                print("DANS DISTORD : " + str(i))
                distorded_image = distortion(image,intensity=optionsValues[i])
                save_img(distorded_image, filename, "_distorded.jpg", output_folder)
                i = i + 1
            else : #dans le cas où il a été coché mais mis a 0% faut augmenter pour s'adapter aux indices de optionsValues
                i = i + 1

        if "brightness" in options:

            # Modifier la luminosité de l'image, image plus lumineuse
            if optionsValues[i] > 0 :
                print("DANS BRIGTH : " + str(i))
                brightness_image = luminosity(image, beta=50, intensity=optionsValues[i])
                save_img(brightness_image, filename, "_brightness.jpg", output_folder)
                i = i + 1
            else : #dans le cas où il a été coché mais mis a 0% faut augmenter pour s'adapter aux indices de optionsValues
                i = i + 1

        if "contrast" in options:

            # Avec du contraste
            if optionsValues[i] > 0 :
                print("DANS CONTRAST : " + str(i))
                contrast_image = contrast(image, alpha=3, intensity=optionsValues[i])
                save_img(contrast_image, filename, "_contrast.jpg", output_folder)
                i = i + 1
            else : #dans le cas où il a été coché mais mis a 0% faut augmenter pour s'adapter aux indices de optionsValues
                i = i + 1

        if "darkness" in options:

            # Avec du contraste et sombre
            if optionsValues[i] > 0 :
                print("DANS DARK : " + str(i))
                darker_contrast_image = darkness(image, intensity=optionsValues[i])
                save_img(darker_contrast_image, filename, "_darker.jpg", output_folder)
                i = i + 1
            else : #dans le cas où il a été coché mais mis a 0% faut augmenter pour s'adapter aux indices de optionsValues
                i = i + 1
