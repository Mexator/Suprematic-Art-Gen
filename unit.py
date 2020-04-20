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
    setup_called = False
    @staticmethod
    def setup_conditions(target, canvas):
        Unit.TARGET = target
        Unit.CANVAS = canvas
        Unit.MAX_PIX_DIF = max(np.sum(target - canvas),
                               np.sum(np.invert(target) - canvas))
        Unit.MAX_CONTRAST = np.linalg.norm([255, 255, 255])

        Unit.OPTIMAL_NUMBER = 7
        Unit.MAX_CDF = geo.distance([0, 0], [512, 512])
        Unit.CENTER_POINT = [len(Unit.TARGET)/2, len(Unit.TARGET[0])/2]
        Unit.MAX_CENTER_DIST = geo.distance([0, 0], Unit.CENTER_POINT)

        Unit.SETUP_CALLED = True

    def __init__(self, parent=None):
        if not Unit.SETUP_CALLED:
            raise Exception("Please, setup conditions first")
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
        figures_pool = deepcopy(self.figures) + deepcopy(other.figures)
        rand.shuffle(figures_pool)
        for figure in figures_pool:
            figure.translate([randint(-20, 20) for i in range(0, 2)])

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
        action = randint(1, 5)
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
            # Move figure
            f = rand.randint(0, len(ret.figures)-1)
            ret.figures[f].translate([randint(-30, 30), randint(-30, 30)])
        elif action == 5:
            f = rand.randint(0, len(ret.figures)-1)
            rot = randint(0, 180)
            ret.figures[f].rotate(rot)
        ret.fitness_val = ret.fitness()
        return ret

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
        figure_number_fitness = 1 - abs(
            len(self.figures)-Unit.OPTIMAL_NUMBER)/Unit.OPTIMAL_NUMBER

        # More intersections - the better
        # AND
        # Contrast between intersecting figures
        contrast_fitness = 0
        figure_intersection_fitness = 0
        for i in range(0, len(self.figures)):
            for j in range(i+1, len(self.figures)):
                if self.figures[i].intersects(self.figures[j]):
                    figure_intersection_fitness += 1
                    contrast_fitness += fit.color_difference(
                        self.figures[i].data.color, self.figures[j].data.color)

        if(figure_intersection_fitness > 0):
            contrast_fitness /= figure_intersection_fitness
            contrast_fitness /= Unit.MAX_CONTRAST
        else:
            contrast_fitness = 1

        max_figure_intersection_fitness = len(
            self.figures)*(len(self.figures) - 1)/2
        # According to Wikipedia
        # https://en.wikipedia.org/wiki/Complete_graph
        if max_figure_intersection_fitness > 1:
            figure_intersection_fitness /= (
                max_figure_intersection_fitness / 2)
        figure_intersection_fitness = min(figure_intersection_fitness, 1)

        approx_fitness = 1 - np.sum(
            Unit.TARGET - self.draw_unit_on(Unit.TARGET)) / Unit.MAX_PIX_DIF

        center_distance_fitness = 0
        for i in range(0, len(self.figures)):
            for j in range(i+1, len(self.figures)):
                center_distance_fitness += geo.distance(
                    self.figures[i].data.center, self.figures[j].data.center
                )
        if(center_distance_fitness != 0):
            center_distance_fitness /= len(self.figures) * \
                (len(self.figures)-1)/2
            center_distance_fitness /= Unit.MAX_CDF

        # average centers closer to image cnter - the better
        spreading_fitness = 0
        for fig in self.figures:
            spreading_fitness += geo.distance(Unit.CENTER_POINT,
                                              fig.data.center)
        spreading_fitness /= len(self.figures)
        spreading_fitness /= Unit.MAX_CENTER_DIST
        spreading_fitness = 1 - spreading_fitness

        # Contrast with bg
        bg_contrast_fitness = 0
        for fig in self.figures:
            bg_contrast_fitness += fit.color_difference(
                Unit.CANVAS[0][0], fig.data.color
            )
        bg_contrast_fitness /= Unit.MAX_CONTRAST
        bg_contrast_fitness /= len(self.figures)

        # Types should be difference
        type_count = []
        for f_type in list(figures.FigureType):
            count = 0
            for figure in self.figures:
                if figure.figure_type == f_type:
                    count += 1
            type_count.append(count)
        ideal_t_c = len(self.figures)/len(list(figures.FigureType))
        type_count = [abs(i - ideal_t_c)/len(self.figures) for i in type_count]
        type_fitness = 1 - np.sum(np.asarray(type_count))

        ret = 2 * figure_number_fitness + figure_intersection_fitness
        ret += center_distance_fitness + spreading_fitness
        ret += bg_contrast_fitness + approx_fitness
        ret += contrast_fitness + type_fitness

        if verbose:
            print("figure_number_fitness = ", figure_number_fitness)
            print("figure_intersection_fitness = ",
                  figure_intersection_fitness)
            print("approx_fitness = ", approx_fitness)
            print("center_distance_fitness = ", center_distance_fitness)
            print("spreading_fitness = ", spreading_fitness)
            print("bg_contrast_fitness = ", bg_contrast_fitness)
            print("contrast_fitness = ", contrast_fitness)
            print("type_fitness = ", type_fitness)
            print("result = ", ret)

        return ret


def unit_comparator_metric(u: Unit):
    return u.fitness_val
