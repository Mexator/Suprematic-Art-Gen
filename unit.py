""""Module that represent selection unit of genetic algorithm"""
from copy import deepcopy
import random as rand
from random import randint
from skimage import io
import numpy as np
import cv2
import figures


def rgba2rgb(rgba, background=(255, 255, 255)):
    row, col, ch = rgba.shape

    if ch == 3:
        return rgba

    assert ch == 4, 'RGBA image has 4 channels.'

    rgb = np.zeros((row, col, 3), dtype='float32')
    r, g, b, a = rgba[:, :, 0], rgba[:, :, 1], rgba[:, :, 2], rgba[:, :, 3]

    a = np.asarray(a, dtype='float32') / 255.0

    R, G, B = background

    rgb[:, :, 0] = r * a + (1.0 - a) * R
    rgb[:, :, 1] = g * a + (1.0 - a) * G
    rgb[:, :, 2] = b * a + (1.0 - a) * B

    return np.asarray(rgb, dtype='uint8')


TARGET_IMAGE = rgba2rgb(io.imread("input/unnamed.png"))
average = TARGET_IMAGE.mean(axis=0).mean(axis=0)
pixels = np.float32(TARGET_IMAGE.reshape(-1, 3))

n_colors = 5
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
flags = cv2.KMEANS_RANDOM_CENTERS

_, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
_, counts = np.unique(labels, return_counts=True)

dominant = np.uint8(palette[np.argmax(counts)])

BLANK_IMAGE = np.full((512, 512, 3), dominant)
INVERSE = np.invert(TARGET_IMAGE)
MAX_PIX_DIF = max(np.sum(TARGET_IMAGE-BLANK_IMAGE),
                  np.sum(INVERSE-BLANK_IMAGE))

MAX_CONTRAST = np.linalg.norm([255, 255, 255])


class Unit:
    """Selection Unit that is represented by "z-buffer" of figures.\\
    Each figure is one of the figure types defined in module figure"""

    def __init__(self, parent=None):
        self.figures = []
        if parent is None:
            self.generate_figures()
            self.fitness_val = self.fitness()

    def generate_figures(self):
        """Fills self with 10 randomly chosen figures"""
        for _ in range(0, 10):
            fig = figures.random_figure()
            self.figures.append(fig)

    def draw_unit_on(self, canvas: np.ndarray):
        """
        Draw all figures of the current unit at the canvas

        Fill pixels of canvas with color of each figure. Last figures overlap
        first ones
        """
        canvas = canvas.copy()
        for figure in self.figures:
            canvas[figure.draw()] = figure.data.color
        return canvas

    def make_children_with(self, other, children_number=2):
        """
        Represent the crossover operation of evolutionary algorithm.

        Produce children_number of children
        """
        children = []
        figures_pool = self.figures + other.figures
        rand.shuffle(figures_pool)

        # Each child receives equal share of parents' figures
        # i.e 1st child receives figures from 0th to (figures_number / children_number)
        # 2nd child receives figures from (figures_number / children_number) to
        share = int(len(figures_pool)/children_number)

        for i in range(0, children_number):
            child = Unit(parent=self)
            child.figures += figures_pool[i*share:(i+1)*share]
            child.fitness_val = child.fitness()
            children.append(child)
        return children

    def mutate(self):
        """
        Represent not in-place mutation

        Randomly changes figures - either shuffles them, add new to existing ones,
        remove one,
        # TODO [or choose 1 figure and changes it via translation, rotation, and color change]
        """
        ret = deepcopy(self)
        action = randint(1, 4)
        if action == 1 and len(ret.figures) > 1:
            # Remove random figure
            to_be_removed = rand.choice(ret.figures)
            ret.figures.remove(to_be_removed)
        elif action == 2:
            # Add random figure
            figure = figures.random_figure()
            ret.figures.append(figure)
        elif action == 3:
            # Change colors
            f = rand.randint(0, len(ret.figures)-1)
            comp = randint(0, 2)
            add = randint(0, 1)
            if add == 0:
                add = -1
            ret.figures[f].data.color[comp] += add * 20
        elif action == 4:
            f = rand.randint(0, len(ret.figures)-1)
            ret.figures[f].translate([randint(-30, 30), randint(-30, 30)])
        ret.fitness_val = ret.fitness(verbose=True)
        return ret

    OPTIMAL_NUMBER = 7
    MAX_CDF = figures.Figure.distance([0, 0], [512, 512])
    CENTER_POINT = [len(TARGET_IMAGE)/2, len(TARGET_IMAGE[0])/2]
    MAX_CENTER_DIST = figures.Figure.distance([0, 0], CENTER_POINT)

    def fitness(self, verbose=False):
        """
        Fitness function

        Returns floating positive number - the хорошесть of the image, by
        considering its:\n
        figures number (7 is optimal);\n
        number of intersections b/w the figures (more - the better);\n
        degree of similarity with original image (more similar - the better) 
        """
        # Delete invisible figures
        to_be_removed = []
        for i in range(len(self.figures)-1, -1, -1):
            for j in range(i-1, -1, -1):
                if self.figures[i].covers(self.figures[j]):
                    to_be_removed.append(self.figures[j])
        for item in set(to_be_removed):
            self.figures.remove(item)

        # Numer of figures closer to optimal - the better
        # figure_number_fitness = 1 / \
        #     (abs(len(self.figures)-Unit.OPTIMAL_NUMBER)+1)
        figure_number_fitness = 1 - abs(
            len(self.figures)-Unit.OPTIMAL_NUMBER)/Unit.OPTIMAL_NUMBER

        # More intersections - the better
        figure_intersection_fitness = 0
        for i in range(0, len(self.figures)):
            for j in range(i+1, len(self.figures)):
                figure_intersection_fitness += self.figures[i].intersects(
                    self.figures[j])
        max_figure_intersection_fitness = len(
            self.figures)*(len(self.figures) - 1)/(2*2)
        # According to Wikipedia
        # https://en.wikipedia.org/wiki/Complete_graph
        if max_figure_intersection_fitness > 1:
            figure_intersection_fitness /= max_figure_intersection_fitness
        figure_intersection_fitness = min(figure_intersection_fitness, 1)

        approx_fitness = 1 - np.sum(
            TARGET_IMAGE - self.draw_unit_on(TARGET_IMAGE)) / MAX_PIX_DIF

        center_distance_fitness = 0
        for i in range(0, len(self.figures)):
            for j in range(i+1, len(self.figures)):
                center_distance_fitness += figures.Figure.distance(
                    self.figures[i].data.center, self.figures[j].data.center
                )
        if(center_distance_fitness != 0):
            center_distance_fitness /= len(self.figures) * \
                (len(self.figures)-1)/2
            center_distance_fitness /= Unit.MAX_CDF

        # average centers closer to image cnter - the better
        spreading_fitness = 0
        for fig in self.figures:
            spreading_fitness += figures.Figure.distance(Unit.CENTER_POINT,
                                                         fig.data.center)
        spreading_fitness /= len(self.figures)
        spreading_fitness /= Unit.MAX_CENTER_DIST
        spreading_fitness = 1 - spreading_fitness

        # Contrast
        contrast_fitness = 0
        for fig in self.figures:
            # TODO write color diff function
            contrast_fitness += figures.Figure.color_difference(
                BLANK_IMAGE[0][0], fig.data.color
            )
        contrast_fitness /= MAX_CONTRAST
        contrast_fitness /= len(self.figures)

        ret = figure_number_fitness + figure_intersection_fitness
        ret += center_distance_fitness + spreading_fitness
        ret += contrast_fitness + approx_fitness

        if verbose:
            print("figure_number_fitness = ", figure_number_fitness)
            print("figure_intersection_fitness = ",
                  figure_intersection_fitness)
            print("approx_fitness = ", approx_fitness)
            print("center_distance_fitness = ", center_distance_fitness)
            print("spreading_fitness = ", spreading_fitness)
            print("contrast_fitness = ", contrast_fitness)
            print("result = ", ret)

        return ret
