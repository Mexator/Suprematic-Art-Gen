""""Module that represent selection unit of genetic algorithm"""
from copy import deepcopy
import random as rand
from random import randint
import numpy as np
import figures
import geometry_helper_functions as geo
import fitness_helper_functions as fit
import constants


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
            fig = figures.random_figure(fit.FITNESS_PARAMETERS["TARGET"])
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
        figures_pool = [i.copy() for i in self.figures] + [i.copy()
                                                           for i in other.figures]
        rand.shuffle(figures_pool)
        for figure in figures_pool:
            figure.translate([randint(-20, 20) for i in range(0, 2)])

        # Each child receives equal share of parents' figures
        # i.e 1st child receives figures from 0th to (figures_number / children_number)
        # 2nd child receives figures from (figures_number / children_number) to
        share = int(len(figures_pool)/children_number)

        for i in range(0, children_number):
            child = Unit(parent=self)
            child.figures = figures_pool[i*share:(i+1)*share]
            child.mutate()
            children.append(child)
        return children

    def mutate(self):
        """
        Represent in-place mutation

        Randomly changes figures - either shuffles them, add new to existing ones,
        remove one,
        """
        action = randint(1, 5)
        if action == 1 and len(self.figures) > 1:
            # Remove random figure
            to_be_removed = rand.choice(self.figures)
            self.figures.remove(to_be_removed)
        elif action == 2:
            # Add random figure
            figure = figures.random_figure(fit.FITNESS_PARAMETERS["TARGET"])
            self.figures.append(figure)
        elif action == 3:
            # Change colors
            f = rand.randint(0, len(self.figures)-1)
            add = randint(0, 1)
            if add == 0:
                add = -1
            self.figures[f].data.color[:] += np.uint8(add * 10)
        elif action == 4:
            # Move figure
            f = rand.randint(0, len(self.figures)-1)
            self.figures[f].translate([randint(-30, 30), randint(-30, 30)])
        elif action == 5:
            f = rand.randint(0, len(self.figures)-1)
            rot = randint(0, 180)
            self.figures[f].rotate(rot)
        self.fitness_val = self.fitness()

        # Delete invisible figures
        fit.remove_invisible(self.figures)
        return self

    def fitness(self, verbose=False):
        """
        Fitness function

        Returns floating positive number - the satisfiability metric of the image, by
        considering its:\n
        figures number\n
        number of intersections b/w the figures (more - the better);\n
        degree of similarity with original image (more similar - the better) 
        """

        # Number of figures closer to optimal - the better
        figure_number_fitness = fit.figure_number_fitness(len(self.figures))

        # More intersections - the better
        # AND
        # Contrast between intersecting figures
        intersection_fitness = fit.intersection_fitness(self.figures)
        
        contrast_fitness = fit.contrast_fitness(self.figures)
        
        approx_fitness = fit.approximation_fitness(
            self.draw_unit_on(fit.FITNESS_PARAMETERS["TARGET"]))

        figure_distance_fitness = fit.figure_distance_fitness(self.figures)

        # average centers closer to image center - the better
        center_distance_fitness = fit.center_distance_fitness(self.figures)

        # Contrast with bg
        bg_contrast_fitness = fit.background_contrast_fitness(self.figures)

        # Types should be different
        type_fitness = fit.type_fitness(self.figures)

        ret =  2 * figure_number_fitness + intersection_fitness
        ret += 2 * figure_distance_fitness + center_distance_fitness
        ret += 2 * bg_contrast_fitness + 2 * approx_fitness
        ret += 2 * contrast_fitness + type_fitness

        if verbose:
            print("figure_number_fitness = ", figure_number_fitness)
            print("figure_intersection_fitness = ",
                  intersection_fitness)
            print("approx_fitness = ", approx_fitness)
            print("figure_distance_fitness = ", figure_distance_fitness)
            print("center_distance_fitness = ", center_distance_fitness)
            print("bg_contrast_fitness = ", bg_contrast_fitness)
            print("contrast_fitness = ", contrast_fitness)
            print("type_fitness = ", type_fitness)
            print("result = ", ret)

        return ret


def unit_comparator_metric(u: Unit):
    return u.fitness_val
