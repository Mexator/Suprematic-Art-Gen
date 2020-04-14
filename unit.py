import random as rand
from skimage import data, io, draw
from random import randint
from figures import Figure, FigureType
from copy import copy


class Unit:
    lifecycle = 100
    def __init__(self, image=None, parent=None):
        self.age = 0
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
            for i in range(0, min(len(child.figures),len(other.figures)*2), 2):
                child.figures[i] = other.figures[int(i/2)]
            children.append(child)
        return children

    def mutate(self):
        action = randint(1, 3)
        if action == 1 and len(self.figures)>1:
            # Remove random figure
            to_be_removed = rand.choice(self.figures)
            self.figures.remove(to_be_removed)
        elif action == 2:
            # Add random figure
            # type = rand.choice(list(FigureType))
            type = FigureType.Circle
            figure = Figure(type)
            self.figures.append(figure)
        elif action == 3:
            # Change order
            rand.shuffle(self.figures)
        # TODO: change color, change position

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
        # Last elements cover first ones
        figure_covering_fitness = 0
        figures = list(reversed(self.figures))
        for i in range(0, len(self.figures)):
            for j in range(i+1, len(self.figures)):
                figure_covering_fitness -= figures[i].covers(
                    figures[j])
        return figure_number_fitness + figure_intersection_fitness + figure_covering_fitness
