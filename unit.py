""""Module that represent selection unit of genetic algorithm"""
from copy import deepcopy
import random as rand
from random import randint
from skimage import io
import numpy as np
import figures

TARGET_IMAGE = io.imread("input/unnamed.png")
INVERSE = np.invert(TARGET_IMAGE)
PIDIF = np.zeros((512, 512, 3), dtype='uint8')
MAX_PIX_DIF = max(np.sum(TARGET_IMAGE-PIDIF), np.sum(INVERSE-PIDIF))
BLANK_IMAGE = np.zeros((512, 512, 3), dtype=int)


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
            # type = rand.choice(list(FigureType))
            figure = figures.random_figure()
            ret.figures.append(figure)
        elif action == 3:
            # Change order
            rand.shuffle(ret.figures)
        elif action == 4:
            # Change colors
            for fig in ret.figures:
                comp = randint(0, 2)
                add = randint(-1, 1)
                fig.data.color[comp] += add * 10
        ret.fitness_val = ret.fitness()
        return ret
        # TODO: change position

    OPTIMAL_NUMBER = 20

    def fitness(self):
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
        for i in range(len(self.figures)-1, 0, -1):
            for j in range(i-1, 0, -1):
                if self.figures[i].covers(self.figures[j]):
                    to_be_removed.append(self.figures[j])
        for item in set(to_be_removed):
            self.figures.remove(item)

        # Numer of figures closer to optimal - the better
        figure_number_fitness = 1 / \
            (abs(len(self.figures)-Unit.OPTIMAL_NUMBER)+1)

        # More intersections - the better
        figure_intersection_fitness = 0
        for i in range(0, len(self.figures)):
            for j in range(i+1, len(self.figures)):
                figure_intersection_fitness += self.figures[i].intersects(
                    self.figures[j])
        max_figure_intersection_fitness = len(
            self.figures)*(len(self.figures) - 1)/2
        # According to Wikipedia
        # https://en.wikipedia.org/wiki/Complete_graph
        if max_figure_intersection_fitness > 1:
            figure_intersection_fitness /= max_figure_intersection_fitness

        approx_fitness = 1 - np.sum(
            TARGET_IMAGE - self.draw_unit_on(TARGET_IMAGE)) / MAX_PIX_DIF

        center_distance_fitness = 0
        for i in range(0, len(self.figures)):
            for j in range(i, len(self.figures)):
                center_distance_fitness += figures.Figure.distance(
                    self.figures[i].data.center, self.figures[j].data.center
                )
        center_distance_fitness = 1 / center_distance_fitness
        center_distance_fitness = 1 - center_distance_fitness

        return figure_number_fitness + figure_intersection_fitness + approx_fitness + center_distance_fitness
