"""Functions to use in counting fitness of unit"""
import numpy as np
from typing import List

from figures import Figure

MAX_COLOR_CONTRAST = np.linalg.norm([255, 255, 255])


def color_difference(color1: np.array, color2: np.array) -> int:
    """Returns contrast metric of two colors"""
    color1 = color1.astype(int)
    color2 = color2.astype(int)
    return np.linalg.norm(color1 - color2)


def remove_invisible(figures: List[Figure]) -> None:
    """Remove invisible figures from list, assuming that last figures overlap
    first ones"""
    to_be_removed = []
    for i in range(len(figures)-1, -1, -1):
        for j in range(i-1, -1, -1):
            if figures[i].covers(figures[j]):
                to_be_removed.append(figures[j])
    for item in set(to_be_removed):
        figures.remove(item)


def figure_number_fitness(n: int) -> float:
    """Returns number (-inf;1] , that reflects how given number is close to optimal
    figures number"""
    return 1 - abs(n-OPTIMAL_NUMBER_OF_FIGURES)/OPTIMAL_NUMBER_OF_FIGURES


OPTIMAL_NUMBER_OF_FIGURES = 7


def intersections_and_contrast_fitness(figures: List[Figure]) -> [float, float]:
    """Returns pair of two floats [0;1] - metrics of degree of intersection of figures
    and color contrast between intersecting figures"""
    figure_intersection_fitness = 0
    contrast_fitness = 0
    for i, figure in enumerate(figures):
        for j in range(i+1, len(figures)):
            if figure.intersects(figures[j]):
                figure_intersection_fitness += 1
                contrast_fitness += color_difference(
                    figure.data.color, figures[j].data.color)

    # Normalize contrast fitness
    if figure_intersection_fitness > 0:
        contrast_fitness /= figure_intersection_fitness
        contrast_fitness /= MAX_COLOR_CONTRAST
    else:
        contrast_fitness = 1

    # If we consider figures as nodes, and their intersections as edges then
    # we can use formula for number of nodes in complete graph, that
    # according to Wikipedia is n(n-1)/2
    # https://en.wikipedia.org/wiki/Complete_graph
    max_intersections = len(figures)*(len(figures) - 1)/2

    if max_intersections > 1:
        figure_intersection_fitness /= max_intersections

    return [figure_intersection_fitness, contrast_fitness]

def max_pixel_difference(target: np.array):
    return np.linalg.norm(target - np.invert(target))

def approximation_fitness(rendered: np.array, target: np.array):
    # approx_fitness = 1 - np.sum(
    # Unit.TARGET - self.draw_unit_on(Unit.TARGET)) / Unit.MAX_PIX_DIF
    difference = target - rendered
    metric = np.linalg.norm(difference)
    metric /= max_pixel_difference(target)
    return 1 - metric
