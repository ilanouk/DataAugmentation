import sys

import cv2
import shutil
import os
from .traitementIntensite import *


def augmentationFile(filename, input_folder, output_folder, options, optionsValues):

    optionsValues = [int(x) for x in optionsValues] #convertir les str en int

    y = 0

    optionNotChecked = [True,True,True,True,True,True,True,True,True,True,True] # pour être sur d'appliquer l'option une seule fois dans le while

    while ( y < len(optionsValues) ):

        # Vérifier si le fichier est une image
        if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png") or filename.endswith(".gif"):
            # Charger l'image avec OpenCV
            image = cv2.imread(os.path.join(input_folder, filename))


            if "flippedX" in options:
                # retournement de l'image en horizontal
                flippedX_image = mirror(image, 1)
                save_img(flippedX_image, filename, "_flippedX.jpg", output_folder)


            if "flippedY" in options:
                # retournement de l'image en vertical
                flippedY_image = mirror(image, 0)
                save_img(flippedY_image, filename, "_flippedY.jpg", output_folder)



            if "rotation" in options and optionNotChecked[0] == True:
                # Effectuer la rotation de l'image de 90 degrés
                if optionsValues[y] > 0 :
                    rotated_image = rotation(image, 90, intensity=optionsValues[y])
                    save_img(rotated_image, filename, "_rotated.jpg", output_folder)
                    optionNotChecked[0] = False



            elif "zoom" in options and optionNotChecked[1] == True:
                # Appliquer le zoom sur l'image
                if optionsValues[y] > 0 :
                    zoomed_image = zoom(image, 4, intensity=optionsValues[y])
                    save_img(zoomed_image, filename, "_zoomed.jpg", output_folder)
                    optionNotChecked[1] = False



            elif "translation" in options and optionNotChecked[2] == True:
                # Translation de l'image
                if optionsValues[y] > 0 :
                    translated_image = translate(image, 300, 300, intensity=optionsValues[y])
                    save_img(translated_image, filename, "_translated.jpg", output_folder)
                    optionNotChecked[2] = False



            elif "noise" in options and optionNotChecked[3] == True:
                # Ajout de bruit gaussien
                if optionsValues[y] > 0 :
                    noise_image = add_gaussian_noise(image, 0, 40, intensity=optionsValues[y])
                    save_img(noise_image, filename, "_noise.jpg", output_folder)
                    optionNotChecked[3] = False



            elif "blur" in options and optionNotChecked[4] == True:
                # Ajout de flou gaussien
                if optionsValues[y] > 0 :
                    blur_image = blur(image, 21, 10, intensity=optionsValues[y])
                    save_img(blur_image, filename, "_blur.jpg", output_folder)
                    optionNotChecked[4] = False



            elif "distortion" in options and optionNotChecked[5] == True:
                # Distorsion de l'image
                if optionsValues[y] > 0 :
                    distorded_image = distortion(image,intensity=optionsValues[y])
                    save_img(distorded_image, filename, "_distorded.jpg", output_folder)
                    optionNotChecked[5] = False

            

            elif "brightness" in options and optionNotChecked[6] == True:
                # Modifier la luminosité de l'image, image plus lumineuse
                if optionsValues[y] > 0 :
                    brightness_image = luminosity(image, beta=50, intensity=optionsValues[y])
                    save_img(brightness_image, filename, "_brightness.jpg", output_folder)
                    optionNotChecked[6] = False



            elif "contrast" in options and optionNotChecked[7] == True:
                # Avec du contraste
                if optionsValues[y] > 0 :
                    contrast_image = contrast(image, alpha=3, intensity=optionsValues[y])
                    save_img(contrast_image, filename, "_contrast.jpg", output_folder)
                    optionNotChecked[7] = False



            elif "darkness" in options and optionNotChecked[8] == True:
                # Avec du contraste et sombre
                if optionsValues[y] > 0 :
                    darker_contrast_image = darkness(image, intensity=optionsValues[y])
                    save_img(darker_contrast_image, filename, "_darker.jpg", output_folder)
                    optionNotChecked[8] = False
        

            
            y += 1
