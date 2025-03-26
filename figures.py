"""Suprematism figures classes"""
from copy import copy
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


class Figure:
    """Base class for figures. Should never be instantiated"""
    MAX_SIZE = [256, 256]
    MIN_SIZE = [30, 30]
    figure_type = None

    class FigureData:
        """General figure data"""
        color: [int, int, int]
        center: [int, int]

        def __init__(self, color: [int, int, int]):
            self.color = color

    def __init__(self):
        self.data = None

    def inside(self, point: [int, int]) -> bool:
        """Check given point to be inside of current figure"""
        vertices = self.data.vertices()

        polygon_area = self.data.area()
        area_from_external_point = geo.pivotal_area(vertices, point)

        return abs(polygon_area - area_from_external_point) < 1e-5

    def translate(self, translation_vector: [int, int]) -> None:
        """Moves figure by translation vector, by changing its center coordinates"""
        self.data.center += np.asarray(translation_vector)
        radius = self.data.radius
        lower_bound = [radius+1, radius+1]
        upper_bound = [(i-1) - radius for i in constants.IMAGE_SIZE]
        self.data.center = np.clip(
            self.data.center, a_min=lower_bound, a_max=upper_bound)

    def delta_scale(self, delta:float):
        tmp = [512 - item for item in self.data.center]
        max_rad = min(list(self.data.center) + tmp + [i/2 for i in Figure.MAX_SIZE])
        self.data.radius += delta
        self.data.radius = min(self.data.radius,max_rad-1)
        self.data.radius = max(self.data.radius,Figure.MIN_SIZE[0])    

    def scale(self, scale: float) -> None:
        """Scales figure by scale times. Clips it to max size, if new size is too large"""
        center = self.data.center
        tmp = [512 - item for item in center]
        max_rad = min(center + tmp + [i/2 for i in Figure.MAX_SIZE])
        self.data.radius *= scale
        self.data.radius = np.clip(self.data.radius, a_min=0, a_max=max_rad)
        if self.data.area_val is not None:
            self.data.area_val = self.data.area()


class Circle(Figure):
    """Circle class"""
    figure_type = FigureType.Circle

    class CircleData(Figure.FigureData):
        """Necessary data to create circle"""
        radius: int
        center: [int, int]

        def __init__(self, radius: int, center: [int, int], color: np.array):
            super(Circle.CircleData, self).__init__(color)
            self.radius = radius
            self.center = center

        def copy(self):
            return Circle.CircleData(self.radius,
                                     [i for i in self.center],
                                     color=self.color[:])

    def __init__(self, data: CircleData):
        super().__init__()
        self.data = data.copy()
        if data is None:
            raise Exception('Data is none')

    def inside(self, point: [int, int]) -> bool:
        """check the point to be inside the figure"""
        return geo.distance(self.data.center, point) < self.data.radius

    def draw(self, scale=1) -> np.ndarray:
        """Returns coordinates of circle that can be used for indexing image to
        fill part of it with color of figure"""
        return draw.disk((self.data.center[1]*scale, self.data.center[0]*scale), self.data.radius*scale)

    def intersects(self, other: Figure) -> bool:
        """check 2 figures for intersection"""
        if other.figure_type == FigureType.Circle:
            center = self.data.center
            other_center = other.data.center
            dist = geo.distance(center, other_center)
            return dist < (self.data.radius + other.data.radius)
        if other.figure_type == FigureType.Rectangle:
            return other.intersects(self)
        return False

    def covers(self, other: Figure) -> bool:
        """check if current figure covers other and makes it invisible"""
        if other.figure_type == FigureType.Circle:
            center = self.data.center
            other_center = other.data.center
            dist = geo.distance(center, other_center)
            radius_1 = self.data.radius
            radius_2 = other.data.radius
            return dist + radius_2 <= radius_1
        if other.figure_type == FigureType.Rectangle:
            vertices = other.data.vertices()
            for i in range(0, len(vertices[0])):
                if not self.inside(vertices[i]):
                    return False
            return True
        return False

    def rotate(self, _) -> None:
        """does nothing, rotation do not make sense for circles"""
        return

    def copy(self):
        return Circle(self.data.copy())


class Rectangle(Figure):
    """Rectangle class"""
    figure_type = FigureType.Rectangle

    count = 0
    count2 = 0

    class RectangleData(Circle.CircleData):
        """Necessary data to create rectangle: circumscribed circle and two angles"""

        def __init__(self, radius: int, center: [int, int], thetas: (float, float), color):
            super().__init__(radius, center, color)
            self.angles = thetas
            self.area_val = None

        def area(self) -> float:
            """returns area of the rectangle"""
            if self.area_val is None:
                self.area_val = geo.pivotal_area(self.vertices())
            return self.area_val

        def vertices(self) -> np.array:
            """returns vertices of the rectangle"""
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

        def copy(self):
            return Rectangle.RectangleData(self.radius, copy(self.center),
                                           copy(self.angles), np.copy(self.color))

    def __init__(self, data: RectangleData):
        super().__init__()
        self.data = data.copy()
        if data is None:
            raise Exception('You should either provide both'
                            'random as false, and data or neither of them')

    def draw(self, scale=1):
        """Returns coordinates of rectangle that can be used for indexing image to
        fill part of it with color of figure"""
        vertices_x = [i[0]*scale for i in self.data.vertices()]
        vertices_y = [i[1]*scale for i in self.data.vertices()]
        return draw.polygon(vertices_y, vertices_x)

    def intersects(self, other: Figure):
        """check 2 figures for intersection"""
        if other.figure_type == FigureType.Circle:
            new_circle = Circle(data=self.data)
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
            for i in range(0, len(vertices)):
                edge = [prev, vertices[i]]
                prev2 = vertices2[-1]
                for j in range(0, len(vertices2)):
                    edge2 = [prev2, vertices2[j]]
                    if geo.line_segments_intersection(edge, edge2):
                        return True
                    prev2 = vertices2[j]
                prev = vertices[i]

        return False

    def covers(self, other: Figure):
        """check if current figure covers other and makes it invisible"""
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

    def rotate(self, degrees: int):
        """rotates self around center on degrees degrees"""
        ang = ((i + degrees)%360 for i in self.data.angles)
        ang = tuple(ang)
        self.data.angles = ang
    

    def copy(self):
        return Rectangle(self.data.copy())


def random_circle(target: np.array, min_rad: int = min(Figure.MIN_SIZE)) -> Circle:
    """creates and returns random circle"""
    center = [randint(1, constants.IMAGE_SIZE[i] - 1) for i in range(0, 2)]
    color = copy(target[center[1], center[0], :])
    tmp = [512 - item for item in center]
    max_rad = min(center + tmp + [i/2 for i in Figure.MAX_SIZE])
    if max_rad < min_rad:
        return random_circle(target, min_rad)

    radius = randint(min_rad, max_rad)
    data = Circle.CircleData(radius, center, color)
    return Circle(data)


def random_rectangle(target: np.array) -> Rectangle:
    """creates and returns random rectangle"""
    circle = random_circle(target, min_rad=50)
    center = circle.data.center
    radius = circle.data.radius
    color = copy(target[center[1], center[0], :])
    angle1 = randint(0, 360)
    angle2 = randint(0, 360)
    if abs(angle1 % 180 - angle2 % 180) < 30:
        angle2 = angle1 + 30
    return Rectangle(Rectangle.RectangleData(radius, center, (angle1, angle2), color))


def random_figure(target: np.array) -> Figure:
    """Returns random  suprematism figure"""
    figures_dict = {
        FigureType.Circle: random_circle(target),
        FigureType.Rectangle: random_rectangle(target)}
    _type = rand.choice(list(FigureType))
    return figures_dict[_type]
