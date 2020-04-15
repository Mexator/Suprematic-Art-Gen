from copy import copy, deepcopy
import random as rand
from random import randint

import figures


class Unit:
    def __init__(self, image=None, parent=None):
        self.age = 0

        if image is None and parent is not None:
            self.image = parent.image
            self.figures = copy(parent.figures)
        elif (parent is None) and image is not None:

            self.figures = []
            self.image = image
            self.generate_figures()
        else:
            raise Exception('At least one of \'image\' or \'parent\' '
                            'parameter should be initialized')
        self.fitness_val = self.fitness()
        self.lifecycle = max(10, self.fitness_val)

    def generate_figures(self):
        for _ in range(0, 10):
            fig = figures.random_figure()
            self.figures.append(fig)

    def draw_unit_on(self, canvas):
        canvas = canvas.copy()
        for figure in self.figures:
            canvas[figure.draw()] = figure.data.color
        return canvas

    def make_children_with(self, other, children_number=1):
        children = []
        for _ in range(0, children_number):
            child = Unit(parent=self)
            for i in range(0, min(len(child.figures), len(other.figures)*2), 2):
                child.figures[i] = other.figures[int(i/2)]
            child.fitness_val = child.fitness()
            child.lifecycle = max(10, child.fitness_val)
            children.append(child)
        return children

    def mutate(self):
        action = randint(1, 3)
        if action == 1 and len(self.figures) > 1:
            # Remove random figure
            to_be_removed = rand.choice(self.figures)
            self.figures.remove(to_be_removed)
        elif action == 2:
            # Add random figure
            # type = rand.choice(list(FigureType))
            figure = figures.random_figure()
            self.figures.append(figure)
        elif action == 3:
            # Change order
            rand.shuffle(self.figures)
        # TODO: change color, change position

    def fitness(self):
        # Delete invisible figures
        to_be_removed = []
        for i in range(len(self.figures)-1, 0, -1):
            for j in range(i-1, 0, -1):
                if(self.figures[i].covers(self.figures[j])):
                    to_be_removed.append(j)
        for item in to_be_removed:
            del self.figures[item]
        
        # Less figures - the better
        figure_number_fitness = 1/len(self.figures)
        # More intersections - the better
        figure_intersection_fitness = 0
        for i in range(0, len(self.figures)):
            for j in range(i+1, len(self.figures)):
                    figure_intersection_fitness += self.figures[i].intersects(
                    self.figures[j])

        return figure_number_fitness + figure_intersection_fitness
