import random as rand
from random import randint
from skimage import draw
from enum import Enum
from numpy import sqrt


class FigureType(Enum):
    Circle = 1
    Rectangle = 2
    Triangle = 3
    Cross = 4


class Figure:
    def __init__(self, type, random=True, color=None, vertices=None,
                 circle_center_x=None, circle_center_y=None, radius=None):
        self.max_size_x = self.max_size_y = 512
        self.type = type
        if random:
            self.color = (randint(0, 255), randint(0, 255), randint(0, 255))
            if type == FigureType.Circle:
                self.center, self.radius = self.random_circle()
        else:
            self.color = color
            if type == FigureType.Circle:
                self.center = [circle_center_x, circle_center_y]
                self.radius = radius

    def draw(self):
        if(self.type == FigureType.Circle):
            return draw.circle(*self.center, self.radius)

    def intersects(self, other):
        if(self.type == FigureType.Circle):
            if(other.type == FigureType.Circle):
                distance = sqrt(
                    (self.center[0]-other.center[0])**2 +
                    (self.center[1]-other.center[1])**2)
                return distance < (self.radius + other.radius)
    
    def covers(self,other):
        if(self.type == FigureType.Circle):
            if(other.type == FigureType.Circle):
                distance = sqrt(
                    (self.center[0]-other.center[0])**2 +
                    (self.center[1]-other.center[1])**2)
                R = self.radius
                r = other.radius
                return distance + r <= R

    def random_circle(self):
        center = [randint(1, self.max_size_x-1) for i in range(0, 2)]
        tmp = [512-item for item in center]
        max_rad = min(center + tmp)
        if max_rad < 10:
            center, radius = self.random_circle()
        else:
            radius = randint(10, max_rad)
        return [center, radius]
