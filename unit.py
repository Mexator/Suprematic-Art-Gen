from skimage import data, io, draw
from random import randint
from figures import Figure, FigureType
from copy import copy


class Unit:
    def __init__(self, image=None, parent=None):
        if (image is None) and (not (parent is None)):
            self.image = copy(parent.image)
            self.figures = copy(parent.figures)
        elif (parent is None) and (not (image is None)):
            self.figures = []
            self.image = image
            self.generate_figures()
        else:
            raise Exception('''At least one of \'image\' or \'parent\' 
                parameter should be initialized''')

    def generate_figures(self):
        for _ in range(0, 10):
            fig = Figure(FigureType.Circle)
            self.figures.append(fig)

    def draw_unit_on(self, canvas):
        canvas = canvas.copy()
        for figure in self.figures:
            canvas[figure.draw()] = figure.color
        return canvas

    def make_children_with(self, other, children_number=1):
        children = []
        for _ in range(0, children_number):
            child = Unit(parent=self)
            for i in range(0, len(child.figures), 2):
                child.figures[i] = other.figures[int(i/2)]
            children.append(child)
        return children

    def fitness(self):
        # Less figures - the better
        figure_number_fitness = 1/len(self.figures)
        # More intersections - the better
        figure_intersection_fitness = 0
        for i in range(0, len(self.figures)):
            for j in range(i+1, len(self.figures)):
                figure_intersection_fitness += self.figures[i].intersects(
                    self.figures[j])
        # Less covers - the better
        figure_covering_fitness = 0
        for i in range(0, len(self.figures)):
            for j in range(i+1, len(self.figures)):
                figure_covering_fitness -= self.figures[i].covers(
                    self.figures[j])
        return figure_number_fitness + figure_intersection_fitness + figure_covering_fitness
