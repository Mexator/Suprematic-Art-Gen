""""Module that represent selection unit of genetic algorithm"""
from copy import copy
import random as rand
from random import randint
from skimage import io
import numpy as np
import figures

TARGET_IMAGE = io.imread("input/unnamed.png")
INVERSE = np.invert(TARGET_IMAGE)
PIDIF = np.zeros((512, 512, 3), dtype='uint8')
for i in range(0, 512):
    for j in range(0, 512):
        for k in range(0, 3):
            PIDIF[i, j, k] = max(TARGET_IMAGE[i, j, k], INVERSE[i, j, k])

MAX_PIX_DIF = np.sum(PIDIF)


class Unit:
    """Selection Unit that is represented by "z-buffer" of figures.\\
    Each figure is one of the figure types defined in module figure"""

    def __init__(self, parent=None):
        if parent is not None:
            self.figures = copy(parent.figures)
        else:
            self.figures = []
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

    def make_children_with(self, other, children_number=1):
        """
        Represent the crossover operation of evolutionary algorithm.

        Produce children_number of children
        """
        children = []
        for _ in range(0, children_number):
            child = Unit(parent=self)
            for i in range(0, min(len(child.figures), len(other.figures)*2), 2):
                child.figures[i] = other.figures[int(i/2)]
            child.fitness_val = child.fitness()
            children.append(child)
        return children

    def mutate(self):
        """
        Represent in-place mutation

        Randomly changes figures - either shuffles them, add new to existing ones,
        remove one,
        # TODO [or choose 1 figure and changes it via translation, rotation, and color change]
        """
        action = randint(1, 3)
        if action == 1 and len(self.figures) > 1:
            # Remove random figure
            to_be_removed = rand.choice(self.figures)
            self.figures.remove(to_be_removed)
            self.fitness_val = self.fitness()
        elif action == 2:
            # Add random figure
            # type = rand.choice(list(FigureType))
            figure = figures.random_figure()
            self.figures.append(figure)
            self.fitness_val = self.fitness()
        elif action == 3:
            # Change order
            rand.shuffle(self.figures)
            self.fitness_val = self.fitness()
        # TODO: change color, change position

    OPTIMAL_NUMBER = 7

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
        if(max_figure_intersection_fitness > 1):
            figure_intersection_fitness /= max_figure_intersection_fitness

        approx_fitness = np.sum(
            TARGET_IMAGE - self.draw_unit_on(TARGET_IMAGE)) / MAX_PIX_DIF

        return figure_number_fitness + figure_intersection_fitness + approx_fitness
