"""Contains preprocessing functions"""
import numpy as np
import cv2


def rgba2rgb(rgba: np.array, background=(255, 255, 255)) -> np.array:
    """Converts image with alpha channel to rgb"""
    # https://stackoverflow.com/questions/50331463/convert-rgba-to-rgb-in-python
    row, column, channel = rgba.shape

    if channel == 3:
        return rgba

    assert channel == 4, 'RGBA image has 4 channels.'

    rgb = np.zeros((row, column, 3), dtype='float32')
    r, g, b, a = rgba[:, :, 0], rgba[:, :, 1], rgba[:, :, 2], rgba[:, :, 3]

    a = np.asarray(a, dtype='float32') / 255.0

    R, G, B = background

    rgb[:, :, 0] = r * a + (1.0 - a) * R
    rgb[:, :, 1] = g * a + (1.0 - a) * G
    rgb[:, :, 2] = b * a + (1.0 - a) * B

    return np.asarray(rgb, dtype='uint8')


def get_dominant_color(image: np.array) -> np.array:
    """Returns dominant color of image"""
    # https://stackoverflow.com/questions/43111029/how-to-find-the-average-colour-of-an-image-in-python-with-opencv
    pixels = np.float32(image.reshape(-1, 3))

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
    flags = cv2.KMEANS_RANDOM_CENTERS

    _, labels, palette = cv2.kmeans(pixels, 1, None, criteria, 10, flags)
    _, counts = np.unique(labels, return_counts=True)

    return np.uint8(palette[np.argmax(counts)])


def get_blank(color: list) -> np.array:
    return np.full((512, 512, 3), color)
