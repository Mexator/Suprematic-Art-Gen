"""Functions to use in counting fitness of unit"""
import numpy as np


def color_difference(color1: np.array, color2: np.array) -> int:
    """Returns contrast metric of two colors"""
    color1 = color1.astype(int)
    color2 = color2.astype(int)
    return np.linalg.norm(color1 - color2)
