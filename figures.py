"""Suprematism figures, and functions that help found fitness"""
import copy
import random as rand
from random import randint
from enum import Enum
from math import sin, cos, radians

from skimage import draw
import numpy as np


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
    """Base class for figures"""
    max_size = [512, 512]
    figure_type = None

    @staticmethod
    def random_color():
        return (randint(50, 255), randint(50, 255), randint(50, 255))

    @staticmethod
    def distance(point1: [int, int], point2: [int, int]):
        p1 = np.array(point1)
        p2 = np.array(point2)
        return np.linalg.norm(p1-p2)

    @staticmethod
    def seg_circle_intersection(circle, segment: [[int, int], [int, int]]):
        # http://doswa.com/2009/07/13/circle-segment-intersectioncollision.html
        # a - segment[0]
        segment_vector = np.array(
            [[segment[1][i] - segment[0][i] for i in range(0, 2)]])
        rel_pos_vector = np.array(
            [[circle.center[i] - segment[0][i] for i in range(0, 2)]])
        seg_unit = segment_vector*1/np.linalg.norm(segment_vector)
        proj_vector_len = rel_pos_vector.dot(np.transpose(seg_unit))
        if proj_vector_len < 0:
            closest = segment[0]
        elif proj_vector_len > np.linalg.norm(segment_vector):
            closest = segment[1]
        else:
            proj_vector = proj_vector_len * seg_unit
            closest = np.array(segment[0]) + proj_vector
        if Figure.distance(closest.reshape(2, ), circle.center) < circle.radius:
            return True
        return False

    @staticmethod
    def triangle_area(p1: [int, int], p2: [int, int], p3: [int, int]):
        char_mat = np.array([
            [p1[0], p1[1], 1],
            [p2[0], p2[1], 1],
            [p3[0], p3[1], 1]
        ])
        return abs(0.5 * np.linalg.det(char_mat))

    def inside(self, point: [int, int]):
        vertices = self.data.vertices()
        prev = vertices[:, 0]
        area_external_pt = 0
        for i in range(1, len(vertices[0])):
            cur = vertices[:, i]
            area_external_pt += Figure.triangle_area(prev, cur, point)
            prev = cur
        area_external_pt += Figure.triangle_area(
            vertices[:, 0], vertices[:, -1], point)

        area_internal_pt = 0
        internal_pt = vertices[:, 0]
        prev = vertices[:, 0]
        for i in range(1, len(vertices[0])):
            cur = vertices[:, i]
            area_internal_pt += Figure.triangle_area(prev, cur, internal_pt)
            prev = cur
        area_internal_pt += Figure.triangle_area(
            vertices[:, 0], vertices[:, -1], internal_pt)

        return (area_external_pt - area_internal_pt) < 1e-5

    @staticmethod
    def rotation_matrix(theta):
        return np.array([
            [cos(theta), -sin(theta)],
            [sin(theta), cos(theta)]
        ])

    @staticmethod
    def line_segments_intersection(seg1: [[int, int], [int, int]],
                                   seg2: [[int, int], [int, int]]) -> bool:
        o1 = np.asarray(seg1[0])
        d1 = np.asarray(seg1[1])-np.asarray(seg1[0])
        o2 = np.asarray(seg2[0])
        d2 = np.asarray(seg2[1])-np.asarray(seg2[0])

        d2_ort = d2.dot(Figure.rotation_matrix(np.pi/2))
        d1_ort = d1.dot(Figure.rotation_matrix(np.pi/2))

        tmp = d1.dot(d2_ort)
        if abs(tmp) <= 1e-10:
            return False
        s = (o2-o1).dot(d2_ort)
        s /= tmp

        tmp = d2.dot(d1_ort)
        if abs(tmp) <= 1e-10:
            return False
        t = (o1-o2).dot(d1_ort)
        t /= tmp

        return s > 0 and s < 1 and t > 0 and t < 1


class Circle(Figure):
    figure_type = FigureType.Circle

    # Necessary data to create circle
    class CircleData:
        radius: int
        center: [int, int]
        color: (int, int, int)

        def __init__(self, r: int, c: [int, int], col: (int, int, int)):
            self.radius = r
            self.center = c
            self.color = col

    def __init__(self, is_random=True, data: CircleData = None):
        if is_random:
            color = Figure.random_color()
            center, radius = self.random_circle()
            self.data = Circle.CircleData(radius, center, color)
        elif data:
            self.data = copy.deepcopy(data)
        else:
            raise Exception('You should either provide both '
                            'random as false, and data or neither of them')

    def inside(self, point: [int, int]):
        return Figure.distance(self.data.center, point) < self.data.radius

    def draw(self):
        return draw.circle(self.data.center[1], self.data.center[0], self.data.radius)

    def translate(self, delta: (int, int)):
        raise NotImplementedError('')

    def rotate(self, degrees: int):
        raise NotImplementedError('')

    def change_color(self, color: (int, int, int)):
        raise NotImplementedError('')

    def intersects(self, other: Figure):
        if other.figure_type == FigureType.Circle:
            center = self.data.center
            other_center = other.data.center
            dist = Figure.distance(center, other_center)
            return dist < (self.data.radius + other.data.radius)
        if other.figure_type == FigureType.Rectangle:
            return other.intersects(self)

    def covers(self, other):
        if other.figure_type == FigureType.Circle:
            center = self.data.center
            other_center = other.data.center
            dist = Figure.distance(center, other_center)
            R = self.data.radius
            r = other.data.radius
            return dist + r <= R
        if other.figure_type == FigureType.Rectangle:
            vertices = other.data.vertices()
            for i in range(0, len(vertices[0])):
                if not self.inside(vertices[:, i]):
                    return False
            return True

    @staticmethod
    def random_circle(min_rad=10):
        center = [randint(1, Figure.max_size[i] - 1) for i in range(0, 2)]
        tmp = [512 - item for item in center]
        max_rad = min(center + tmp)
        if max_rad < min_rad:
            center, radius = Circle.random_circle()
        else:
            radius = randint(min_rad, max_rad)
        return [center, radius]


class Rectangle(Figure):
    figure_type = FigureType.Rectangle

    # Necessary data to create rectangle:
    # circumscribed circle and two angles
    class RectangleData(Circle.CircleData):
        angles: (float, float)

        def __init__(self, r: int, c: [int, int], col: (int, int, int), thetas: (float, float)):
            super().__init__(r, c, col)
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
            return np.array([vertices_x, vertices_y])

    def __init__(self, is_random=True, data: RectangleData = None):
        if is_random:
            color = Figure.random_color()
            center, radius = Circle.random_circle(min_rad=30)
            angle1 = randint(0, 360)
            angle2 = randint(0, 360)
            if abs(angle1 % 180 - angle2 % 180) < 30:
                angle2 = angle1 + 30
            self.data = Rectangle.RectangleData(
                radius, center, color, (angle1, angle2))
        elif data:
            self.data = copy.deepcopy(data)
        else:
            raise Exception('You should either provide both'
                            'random as false, and data or neither of them')

    def draw(self):
        vertices_x, vertices_y = self.data.vertices()
        return draw.polygon(vertices_y, vertices_x)

    def translate(self, delta: (int, int)):
        raise NotImplementedError('')

    def rotate(self, degrees: int):
        raise NotImplementedError('')

    def change_color(self, color: (int, int, int)):
        raise NotImplementedError('')

    def intersects(self, other: Figure):
        if other.figure_type == FigureType.Circle:
            vertices = self.data.vertices()
            prev = vertices[:, 0]
            for i in range(1, len(vertices[0])):
                cur = vertices[:, i]
                if Figure.seg_circle_intersection(other.data, [prev, cur]):
                    return True
                prev = cur
            return Figure.seg_circle_intersection(
                other.data, [vertices[:, -1], vertices[:, 0]])

        if other.figure_type == FigureType.Rectangle:
            vertices = other.data.vertices()
            vertices2 = self.data.vertices()
            prev = vertices[:, len(vertices[0])-1]
            for i in range(0, len(vertices[0])):
                edge = [prev, vertices[:, i]]
                prev2 = vertices2[:, len(vertices2[0])-1]
                for j in range(0, len(vertices2[0])):
                    edge2 = [prev2, vertices2[:, j]]
                    if Figure.line_segments_intersection(edge, edge2):
                        return True
                    prev2 = vertices2[:, j]
                prev = vertices[:, i]

        return False

    def covers(self, other: Figure):
        if other.figure_type == FigureType.Circle:
            if self.inside(other.data.center):
                vertices = self.data.vertices()
                # If at least 1 vertice outside- false
                for i in range(0, len(vertices[0])):
                    if not other.inside(vertices[:, i]):
                        return False
                return True
            return False
        if other.figure_type == FigureType.Rectangle:
            vertices = other.data.vertices()
            for i in range(0, len(vertices[0])):
                if not self.inside(vertices[:, i]):
                    return False
            return True
        return False
