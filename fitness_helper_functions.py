"""Functions to use in counting fitness of unit"""
import numpy as np
from typing import List
from collections import Counter

from figures import Figure, FigureType
import geometry_helper_functions as geo
import constants

MAX_COLOR_CONTRAST = np.linalg.norm([255, 255, 255])
MAX_CENTER_DISTANCE = np.linalg.norm(np.array(Figure.MIN_SIZE) * 2 -
                                     np.array(constants.IMAGE_SIZE))
CENTER_POINT = np.asarray([constants.IMAGE_WIDTH/2, constants.IMAGE_HEIGHT/2])

NO_SETUP_EXCEPTION = Exception("Call setup_fitness_parameters() first")

FITNESS_PARAMETERS = {}


def setup_fitness_parameters(
        target_image: np.array,
        background_color: np.array,
        optimal_figures_number: int = 7):
    FITNESS_PARAMETERS["OPTIMAL_NUMBER_OF_FIGURES"] = optimal_figures_number
    FITNESS_PARAMETERS["TARGET"] = target_image
    FITNESS_PARAMETERS["MAX_PIXEL_DIFFERENCE"] = get_max_pixel_difference(
        target_image)
    FITNESS_PARAMETERS["CANVAS_COLOR"] = background_color
    FITNESS_PARAMETERS["MAX_BACKGROUND_CONTRAST"] = max(np.linalg.norm(background_color),
                                                        np.linalg.norm(np.invert(background_color)))


def color_difference(color1: np.array, color2: np.array) -> int:
    """Return contrast metric of two colors"""
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
    """Return number (-inf;1] , that reflects how given number is close to optimal
    figures number"""
    if not "OPTIMAL_NUMBER_OF_FIGURES" in FITNESS_PARAMETERS:
        raise NO_SETUP_EXCEPTION
    optimal = FITNESS_PARAMETERS["OPTIMAL_NUMBER_OF_FIGURES"]
    return 1 - abs(n-optimal)/optimal


def intersections_and_contrast_fitness(figures: List[Figure]) -> [float, float]:
    """Return pair of two floats [0;1] - metrics of degree of intersection of figures
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


def get_max_pixel_difference(target: np.array):
    """Helper fuction - return maximal rate of difference for given image"""
    return np.linalg.norm(target - np.invert(target))


def approximation_fitness(rendered: np.array):
    """Return number [0;1]: rate of similarity between two raster images"""
    if (not "TARGET" in FITNESS_PARAMETERS) or \
            (not "MAX_PIXEL_DIFFERENCE" in FITNESS_PARAMETERS):
        raise NO_SETUP_EXCEPTION
    target = FITNESS_PARAMETERS["TARGET"]
    max_pixel_difference = FITNESS_PARAMETERS["MAX_PIXEL_DIFFERENCE"]
    # approx_fitness = 1 - np.sum(
    # Unit.TARGET - self.draw_unit_on(Unit.TARGET)) / Unit.MAX_PIX_DIF
    difference = target - rendered
    metric = np.linalg.norm(difference)
    metric /= max_pixel_difference
    return 1 - metric


def figure_distance_fitness(figures: List[Figure]):
    """Return number [0;1]: that reflects how much figures from the list
    far from each other"""
    center_distance_sum = 0
    for i, figure in enumerate(figures):
        for j in range(i+1, len(figures)):
            center_distance_sum += geo.distance(
                figure.data.center, figures[j].data.center)

    metric = 1
    if center_distance_sum:
        number_of_distances = len(figures) * (len(figures)-1) / 2
        metric = center_distance_sum / number_of_distances
        metric /= MAX_CENTER_DISTANCE

    return metric


def type_fitness(figures: List[Figure]):
    """Return number from [0;1]: the metric based on divergense of figure types
    in the list of figures"""
    types = map(lambda x: x.figure_type, figures)

    type_count = Counter(types).values()
    ideal_type_count = len(figures)/len(FigureType)
    type_count = [abs(i - ideal_type_count)/len(figures) for i in type_count]
    return 1 - sum(type_count)


def center_distance_fitness(figures: List[Figure]):
    distance_sum = 0
    for fig in figures:
        distance_sum += geo.distance(CENTER_POINT, fig.data.center)
    average_distance = distance_sum / len(figures)
    metric = average_distance / MAX_CENTER_DISTANCE
    return 1 - metric


def background_contrast_fitness(figures: List[Figure]):
    if (not "CANVAS_COLOR" in FITNESS_PARAMETERS) or \
            (not "MAX_BACKGROUND_CONTRAST" in FITNESS_PARAMETERS):
        raise NO_SETUP_EXCEPTION
    background_color = FITNESS_PARAMETERS["CANVAS_COLOR"]
    max_bg_contrast = FITNESS_PARAMETERS["MAX_BACKGROUND_CONTRAST"]
    difference_sum = 0
    for fig in figures:
        difference_sum += color_difference(
            background_color, fig.data.color)
    average_difference = difference_sum /  len(figures)
    return average_difference/max_bg_contrast
