"""Suprematism figures, and functions that help found fitness"""
import copy
import random as rand
from random import randint
from enum import Enum
from math import sin, cos, radians
from skimage import draw
import numpy as np

import unit
import constants
import geometry_helper_functions as geo


class FigureType(Enum):
    """Suprematism figure types"""
    Circle = 1
    Rectangle = 2
    # Triangle = 3
    # Cross = 4


def random_figure():
    """Returns random  suprematism figure"""
    _type = rand.choice(list(FigureType))
    if _type == FigureType.Circle:
        return Circle()
    if _type == FigureType.Rectangle:
        return Rectangle()
    return None


class Figure:
    """Base class for figures. Should never be instantiated"""
    max_size = [256, 256]
    figure_type = None

    def __init__(self):
        self.data = None

    @staticmethod
    def color_difference(col1, col2):
        """Returns contrast metric of two colors"""
        col1 = col1.astype(int)
        col2 = col2.astype(int)
        color_diff = [abs(i) for i in col1 - col2]
        return np.linalg.norm(color_diff)

    def inside(self, point: [int, int]):
        vertices = self.data.vertices()
        prev = vertices[0]
        area_external_pt = 0
        for i in range(len(vertices)):
            cur = vertices[i]
            area_external_pt += geo.triangle_area(prev, cur, point)
            prev = cur
        area_external_pt += geo.triangle_area(
            vertices[0], vertices[-1], point)

        area_internal_pt = 0
        internal_pt = vertices[0]
        prev = vertices[0]
        for i in range(1, len(vertices[0])):
            cur = vertices[i]
            area_internal_pt += geo.triangle_area(prev, cur, internal_pt)
            prev = cur
        area_internal_pt += geo.triangle_area(
            vertices[0], vertices[-1], internal_pt)

        return (area_external_pt - area_internal_pt) < 1e-5

    def translate(self, translation_vector):
        self.data.center += np.asarray(translation_vector)
        rad = self.data.radius
        for i in range(0, len(self.data.center)):
            if self.data.center[i] + rad > constants.IMAGE_SIZE[i]:
                self.data.center[i] = constants.IMAGE_SIZE[i]-rad
            if self.data.center[i] - rad < 0:
                self.data.center[i] = rad
    
    def scale(self, scale):
        self.data.radius *= scale


class Circle(Figure):
    figure_type = FigureType.Circle

    # Necessary data to create circle
    class CircleData:
        radius: int
        center: [int, int]
        color: [int, int, int]

        def __init__(self, r: int, c: [int, int]):
            self.radius = r
            self.center = c
            self.color = unit.Unit.TARGET[c[0], c[1], :]

    def __init__(self, is_random=True, data: CircleData = None):
        if is_random:
            center, radius = self.random_circle()
            self.data = Circle.CircleData(radius, center)
        elif data:
            self.data = copy.deepcopy(data)
        else:
            raise Exception('You should either provide both '
                            'random as false, and data or neither of them')

    def inside(self, point: [int, int]):
        return geo.distance(self.data.center, point) < self.data.radius

    def draw(self):
        return draw.circle(self.data.center[1], self.data.center[0], self.data.radius)

    def change_color(self, color: [int, int, int]):
        raise NotImplementedError('')

    def intersects(self, other: Figure):
        if other.figure_type == FigureType.Circle:
            center = self.data.center
            other_center = other.data.center
            dist = geo.distance(center, other_center)
            return dist < (self.data.radius + other.data.radius)
        if other.figure_type == FigureType.Rectangle:
            return other.intersects(self)

    def covers(self, other):
        if other.figure_type == FigureType.Circle:
            center = self.data.center
            other_center = other.data.center
            dist = geo.distance(center, other_center)
            R = self.data.radius
            r = other.data.radius
            return dist + r <= R
        if other.figure_type == FigureType.Rectangle:
            vertices = other.data.vertices()
            for i in range(0, len(vertices[0])):
                if not self.inside(vertices[i]):
                    return False
            return True

    @staticmethod
    def random_circle(min_rad=30):
        center = [randint(1, constants.IMAGE_SIZE[i] - 1) for i in range(0, 2)]
        tmp = [512 - item for item in center]
        max_rad = min(center + tmp + [i/2 for i in Figure.max_size])
        if max_rad < min_rad:
            center, radius = Circle.random_circle()
        else:
            radius = randint(min_rad, max_rad)
        return [center, radius]
    
    def rotate(self, degrees):
        pass


class Rectangle(Figure):
    figure_type = FigureType.Rectangle

    # Necessary data to create rectangle:
    # circumscribed circle and two angles
    class RectangleData(Circle.CircleData):
        def __init__(self, r: int, c: [int, int], thetas: (float, float)):
            super().__init__(r, c)
            self.angles = thetas

        def vertices(self):
            vertices_x = []
            vertices_y = []
            center = self.center
            vertices_x += [center[0] + self.radius *
                           sin(radians(i)) for i in self.angles]
            vertices_x += [center[0] + self.radius *
                           sin(radians(i+180)) for i in self.angles]

            vertices_y += [center[1] + self.radius *
                           cos(radians(i)) for i in self.angles]
            vertices_y += [center[1] + self.radius *
                           cos(radians(i+180)) for i in self.angles]

            ret = []
            for i, item in enumerate(vertices_x):
                ret.append([item, vertices_y[i]])

            return np.asarray(ret)

    def __init__(self, is_random=True, data: RectangleData = None):
        if is_random:
            center, radius = Circle.random_circle(min_rad=50)
            angle1 = randint(0, 360)
            angle2 = randint(0, 360)
            if abs(angle1 % 180 - angle2 % 180) < 30:
                angle2 = angle1 + 30
            self.data = Rectangle.RectangleData(
                radius, center, (angle1, angle2))
        elif data:
            self.data = copy.deepcopy(data)
        else:
            raise Exception('You should either provide both'
                            'random as false, and data or neither of them')

    def draw(self):
        vertices_x = [i[0] for i in self.data.vertices()]
        vertices_y = [i[1] for i in self.data.vertices()]
        return draw.polygon(vertices_y, vertices_x)

    def change_color(self, color: (int, int, int)):
        raise NotImplementedError('')

    def intersects(self, other: Figure):
        if other.figure_type == FigureType.Circle:
            new_circle = Circle()
            new_circle.data = self.data
            if not new_circle.intersects(other):
                return False
            vertices = self.data.vertices()
            prev = vertices[0]
            for i in range(1, len(vertices)):
                cur = vertices[i]
                if geo.seg_circle_intersection(other.data, [prev, cur]):
                    return True
                prev = cur
            return geo.seg_circle_intersection(
                other.data, [vertices[-1], vertices[0]])

        if other.figure_type == FigureType.Rectangle:
            vertices = other.data.vertices()
            vertices2 = self.data.vertices()
            prev = vertices[-1]
            for i in range(0, len(vertices[0])):
                edge = [prev, vertices[i]]
                prev2 = vertices2[-1]
                for j in range(0, len(vertices2[0])):
                    edge2 = [prev2, vertices2[j]]
                    if geo.line_segments_intersection(edge, edge2):
                        return True
                    prev2 = vertices2[j]
                prev = vertices[i]

        return False

    def covers(self, other: Figure):
        if other.figure_type == FigureType.Circle:
            if self.inside(other.data.center):
                vertices = self.data.vertices()
                # If at least 1 vertice outside- false
                for i in range(0, len(vertices[0])):
                    if not other.inside(vertices[i]):
                        return False
                return True
            return False
        if other.figure_type == FigureType.Rectangle:
            vertices = other.data.vertices()
            for i in range(0, len(vertices[0])):
                if not self.inside(vertices[i]):
                    return False
            return True
        return False
    
    def rotate(self, degrees):
        for i in self.data.angles:
            i += degrees
