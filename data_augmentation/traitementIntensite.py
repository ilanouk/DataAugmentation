import cv2
import shutil
import os
import numpy as np


def rotation(img, angle=0, coord=None, intensity=50):
    """
    Applique une rotation à une image.

    :param img: L'image à faire pivoter.
    :type img: numpy.ndarray
    :param angle: L'angle de rotation en degrés (par défaut : 0).
    :type angle: float
    :param coord: Les coordonnées du point de pivot de l'image (par défaut : le centre de l'image).
    :type coord: tuple (int, int)
    :param intensity: L'intensité de la rotation, un nombre entre 0 et 100 (par défaut : 100).
    :type intensity: int
    :return: L'image pivotée.
    :rtype: numpy.ndarray
    """
    y, x = [i / 2 for i in img.shape[:-1]] if coord is None else coord[::-1]

    intensity = max(intensity, 0)
    angle = int(angle * intensity / 100)

    rotation_mat = cv2.getRotationMatrix2D((x, y), angle, 1)
    zoomedImg = cv2.warpAffine(img, rotation_mat, img.shape[1::-1])

    return zoomedImg


def zoom(img, zoom=1, coord=None, intensity=50):
    """
    Applique un zoom à une image.

    :param img: L'image à zoomer.
    :type img: numpy.ndarray
    :param zoom: Le facteur de zoom (par défaut : 1).
    :type zoom: float
    :param coord: Les coordonnées du point de pivot de l'image (par défaut : le centre de l'image).
    :type coord: tuple (int, int)
    :param intensity: L'intensité du zoom, un nombre entre 0 et 100 (par défaut : 100).
    :type intensity: int
    :return: L'image zoomée.
    :rtype: numpy.ndarray
    """
    y, x = [i / 2 for i in img.shape[:-1]] if coord is None else coord[::-1]

    intensity = max(intensity, 0)
    zoom = int(zoom * intensity / 100)

    rotation_mat = cv2.getRotationMatrix2D((x, y), 0, zoom)
    zoomedImg = cv2.warpAffine(img, rotation_mat, img.shape[1::-1])

    return zoomedImg


def translate(img, x, y, intensity=50):
    """
    Applique une translation à une image.

    :param img: L'image à translater.
    :type img: numpy.ndarray
    :param x: La distance de translation en pixels sur l'axe des x.
    :type x: int
    :param y: La distance de translation en pixels sur l'axe des y.
    :type y: int
    :param intensity: L'intensité de la translation, un nombre entre 0 et 100 (par défaut : 100).
    :type intensity: int
    :return: L'image translatée.
    :rtype: numpy.ndarray
    """
    intensity = max(intensity, 0)
    x = int(x * intensity / 100)
    y = int(y * intensity / 100)

    # Calcul de la matrice de translation
    translation_matrix = np.float32([[1, 0, x], [0, 1, y]])
    # Application de la matrice de translation à l'image
    translated_image = cv2.warpAffine(img, translation_matrix, (img.shape[0], img.shape[1]))
    return translated_image


def mirror(img, direction):
    """
    Applique une symétrie miroir à une image.

    :param img: L'image à symétriser.
    :type img: numpy.ndarray
    :param direction: La direction de la symétrie miroir (0 pour une symétrie horizontale, 1 pour une symétrie verticale).
    :type direction: int
    :return: L'image symétrisée.
    :rtype: numpy.ndarray
    """
    return cv2.flip(img, direction)


def add_gaussian_noise(image, mean=0, stddev=10, intensity=50):
    """
    Ajoute du bruit gaussien à une image.

    :param image: L'image à laquelle ajouter du bruit.
    :type image: numpy.ndarray
    :param intensity: L'intensité de l'effet de bruit (0-100) (par défaut : 50).
    :type intensity: int
    :param mean: La moyenne de la distribution gaussienne (par défaut : 0).
    :type mean: float
    :param stddev: L'écart-type de la distribution gaussienne (par défaut : 10).
    :type stddev: float

    :return: L'image avec le bruit gaussien ajouté.
    :rtype: numpy.ndarray
    """

    # Calcul de la moyenne et de l'écart-type en fonction de l'intensité
    mean = mean * intensity / 100
    stddev = stddev * intensity / 100

    # Génération de la matrice de bruit
    shape = image.shape
    noise = np.random.normal(mean, stddev, shape)

    # Ajout du bruit à l'image
    noise_image = np.clip(image + noise, 0, 255).astype(np.uint8)

    return noise_image


def blur(image, kernel_size=5, sigma=0, intensity=50):
    """
    Ajoute un flou gaussien à une image.
    source : https://docs.opencv.org/4.x/d4/d13/tutorial_py_filtering.html

    :param image: L'image à laquelle ajouter le flou.
    :type image: numpy.ndarray
    :param kernel_size: La taille du noyau du filtre gaussien (par défaut : 5), elle doit être positive et impaire.
    :type kernel_size: int
    :param sigma: L'écart-type de la distribution gaussienne (par défaut : 0).
    :type sigma: float

    :return: L'image avec le flou gaussien appliqué.
    :rtype: numpy.ndarray
    """
    kernel_size = int(kernel_size * intensity / 100)
    sigma = int(sigma * intensity / 100)
    if kernel_size % 2 == 0:
        kernel_size += 1
    # Appliquer un filtre gaussien à l'image
    blurred_image = cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma)

    return blurred_image


def distortion(image, k1=2, k2=-0.6, p1=0.006, p2=-0.003, intensity=50):
    """
    Applique une distorsion radiale et tangentielle à l'image.
    source : https://docs.opencv.org/4.x/dc/dbb/tutorial_py_calibration.html

    :param image: L'image à distordre.
    :type image: numpy.ndarray
    :param k1: Le coefficient de distorsion radiale k1 (par défaut : 0.5).
    :type k1: float
    :param k2: Le coefficient de distorsion radiale k2 (par défaut : -0.2).
    :type k2: float
    :param p1: Le coefficient de distorsion tangentielle p1 (par défaut : 0.002).
    :type p1: float
    :param p2: Le coefficient de distorsion tangentielle p2 (par défaut : -0.001).
    :type p2: float
    :return: L'image distordue.
    :rtype: numpy.ndarray
    """

    k1 = k1 * intensity / 100
    k2 = k2 * intensity / 100
    p1 = p1 * intensity / 100
    p2 = p2 * intensity / 100

    h, w = image.shape[:2]

    # Définition des coefficients de distorsion
    dist_coeffs = np.zeros((4, 1))
    dist_coeffs[0, 0] = k1
    dist_coeffs[1, 0] = k2
    dist_coeffs[2, 0] = p1
    dist_coeffs[3, 0] = p2

    # Calcul des matrices de transformation
    focal_length = w
    center = (w / 2, h / 2)
    camera_matrix = np.array([[focal_length, 0, center[0]],
                              [0, focal_length, center[1]],
                              [0, 0, 1]], dtype=np.float32)

    # Application de la distorsion a l aide du tableua de distortione et de la matrice camera
    distorted_image = cv2.undistort(image, camera_matrix, dist_coeffs)

    return distorted_image


def luminosity(image, beta, intensity=50):
    """
    Ajuste la luminosité et le contraste d'une image en utilisant une transformation linéaire.

    La fonction multiplie chaque pixel de l'image par alpha et ajoute beta à chaque pixel.
    Ensuite, la fonction applique la valeur absolue de chaque pixel
    et retourne l'image résultante

    :param image: L'image à modifier.
    :type image: numpy.ndarray
    :param alpha: Paramètre pour contrôler le contraste. Une valeur supérieure à 1 augmente le contraste, une valeur inférieure à 1 le diminue.
    :type alpha: float
    :param beta: Paramètre pour contrôler la luminosité. Une valeur supérieure à 0 augmente la luminosité, une valeur inférieure à 0 la diminue.
    :type beta: float
    :return: L'image modifiée.
    :rtype: numpy.ndarray
    """

    beta = int(beta * intensity / 100)

    adjusted = cv2.convertScaleAbs(image, alpha=1.0, beta=beta)

    return adjusted


def contrast(image, alpha, intensity=50):
    """
    Ajuste la luminosité et le contraste d'une image en utilisant une transformation linéaire.

    La fonction multiplie chaque pixel de l'image par alpha et ajoute beta à chaque pixel.
    Ensuite, la fonction applique la valeur absolue de chaque pixel
    et retourne l'image résultante

    :param image: L'image à modifier.
    :type image: numpy.ndarray
    :param alpha: Paramètre pour contrôler le contraste. Une valeur supérieure à 1 augmente le contraste, une valeur inférieure à 1 le diminue.
    :type alpha: float
    :param beta: Paramètre pour contrôler la luminosité. Une valeur supérieure à 0 augmente la luminosité, une valeur inférieure à 0 la diminue.
    :type beta: float
    :return: L'image modifiée.
    :rtype: numpy.ndarray
    """
    alpha = alpha * intensity / 100

    adjusted = cv2.convertScaleAbs(image, alpha=alpha, beta=0)

    return adjusted


def darkness(image, intensity=50):
    """
    Ajuste la luminosité et le contraste d'une image en utilisant une transformation linéaire.

    La fonction multiplie chaque pixel de l'image par alpha et ajoute beta à chaque pixel.
    Ensuite, la fonction applique la valeur absolue de chaque pixel
    et retourne l'image résultante

    :param image: L'image à modifier.
    :type image: numpy.ndarray
    :param alpha: Paramètre pour contrôler le contraste. Une valeur supérieure à 1 augmente le contraste, une valeur inférieure à 1 le diminue.
    :type alpha: float
    :param beta: Paramètre pour contrôler la luminosité. Une valeur supérieure à 0 augmente la luminosité, une valeur inférieure à 0 la diminue.
    :type beta: float
    :return: L'image modifiée.
    :rtype: numpy.ndarray
    """

    alpha = 1.08 - intensity / 100

    adjusted = cv2.convertScaleAbs(image, alpha=alpha, beta=30)

    return adjusted


def save_img(img, filename, name, output_folder):
    """
    Sauvegarde une image modifiée dans un dossier de sortie.

    :param img: L'image modifiée à sauvegarder.
    :type img: numpy.ndarray
    :param filename: Le nom de fichier de l'image d'origine.
    :type filename: str
    :param name: Le suffixe à ajouter au nom de fichier de l'image modifiée.
    :type name: str
    :param output_folder: Le chemin vers le dossier de sortie.
    :type output_folder: str

    :return: None
    """

    # Sauvegarder la nouvelle image dans le même dossier avec un nouveau nom
    output_filename = os.path.splitext(filename)[0] + name
    output_path = os.path.join(output_folder, output_filename)
    cv2.imwrite(output_path, img)
