"""Suprematism figures classes"""
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


class Figure:
    """Base class for figures. Should never be instantiated"""
    MAX_SIZE = [256, 256]
    figure_type = None

    class FigureData:
        """General figure data"""
        color: [int, int, int]
        center: [int, int]

        def __init__(self, color: [int, int, int] = None):
            if color is None:
                color = unit.Unit.TARGET[self.center[0], self.center[1], :]
            self.color = color

    def __init__(self):
        self.data = None

    def inside(self, point: [int, int]) -> bool:
        """Check given point to be inside of current figure"""
        vertices = self.data.vertices()

        polygon_area = geo.pivotal_area(vertices)
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

    def scale(self, scale: float) -> None:
        """Scales figure by scale times. Clips it to max size, if new size is too large"""
        center = self.data.center
        tmp = [512 - item for item in center]
        max_rad = min(center + tmp + [i/2 for i in Figure.MAX_SIZE])
        self.data.radius *= scale
        self.data.radius = np.clip(self.data.radius, a_min=0, a_max=max_rad)


class Circle(Figure):
    """Circle class"""
    figure_type = FigureType.Circle

    class CircleData(Figure.FigureData):
        """Necessary data to create circle"""
        radius: int
        center: [int, int]

        def __init__(self, radius: int, center: [int, int]):
            self.radius = radius
            self.center = center
            super(Circle.CircleData, self).__init__()

    def __init__(self, data: CircleData):
        super().__init__()
        self.data = copy.deepcopy(data)
        if data is None:
            raise Exception('Data is none')

    def inside(self, point: [int, int]) -> bool:
        """check the point to be inside the figure"""
        return geo.distance(self.data.center, point) < self.data.radius

    def draw(self) -> np.ndarray:
        """Returns coordinates of circle that can be used for indexing image to
        fill part of it with color of figure"""
        return draw.circle(self.data.center[1], self.data.center[0], self.data.radius)

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


class Rectangle(Figure):
    """Rectangle class"""
    figure_type = FigureType.Rectangle

    class RectangleData(Circle.CircleData):
        """Necessary data to create rectangle: circumscribed circle and two angles"""

        def __init__(self, r: int, c: [int, int], thetas: (float, float)):
            super().__init__(r, c)
            self.angles = thetas

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

    def __init__(self, data: RectangleData):
        super().__init__()
        self.data = copy.deepcopy(data)
        if data is None:
            raise Exception('You should either provide both'
                            'random as false, and data or neither of them')

    def draw(self):
        """Returns coordinates of rectangle that can be used for indexing image to
        fill part of it with color of figure"""
        vertices_x = [i[0] for i in self.data.vertices()]
        vertices_y = [i[1] for i in self.data.vertices()]
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
        for i in self.data.angles:
            i += degrees


def random_circle(min_rad: int = 30) -> Circle:
    """creates and returns random circle"""
    center = [randint(1, constants.IMAGE_SIZE[i] - 1) for i in range(0, 2)]
    tmp = [512 - item for item in center]
    max_rad = min(center + tmp + [i/2 for i in Figure.MAX_SIZE])
    if max_rad < min_rad:
        return random_circle()

    radius = randint(min_rad, max_rad)
    data = Circle.CircleData(radius, center)
    return Circle(data)


def random_rectangle() -> Rectangle:
    """creates and returns random rectangle"""
    circle = random_circle(min_rad=50)
    center = circle.data.center
    radius = circle.data.radius
    angle1 = randint(0, 360)
    angle2 = randint(0, 360)
    if abs(angle1 % 180 - angle2 % 180) < 30:
        angle2 = angle1 + 30
    return Rectangle(Rectangle.RectangleData(radius, center, (angle1, angle2)))


def random_figure() -> Figure:
    """Returns random  suprematism figure"""
    figures_dict = {
        FigureType.Circle: random_circle(),
        FigureType.Rectangle: random_rectangle()}
    _type = rand.choice(list(FigureType))
    return figures_dict[_type]
