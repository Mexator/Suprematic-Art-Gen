from random import randint
from skimage import draw
from enum import Enum
from numpy import sqrt
import copy

class FigureType(Enum):
    Circle = 1
    Rectangle = 2
    Triangle = 3
    Cross = 4


class Figure:
    max_size = [512,512]
    figure_type = None

    def __init__(self, random=True, data=None):
        raise NotImplementedError('')

    def draw(self):
        raise NotImplementedError('')

    def center(self):
        raise NotImplementedError('')
    def translate(self,delta:(int,int)):
        raise NotImplementedError('')
    def rotate(self,degrees:int):
        raise NotImplementedError('')
    def change_color(self, color:(int,int,int)):
        raise NotImplementedError('')

    def intersects(self,other):
        raise NotImplementedError('')
    def covers(self,other):
        raise NotImplementedError('')


class Circle(Figure):
    figure_type = FigureType.Circle

    # Necessary data to create circle
    class CircleData:
        radius:int
        center:[int,int]
        color:(int,int,int)
        def __init__(self, r:int,c:[int,int],col:(int,int,int)):
            self.radius = r
            self.center = c
            self.color = col

    def __init__(self, is_random=True, data:CircleData=None):
        if is_random:
            color = (randint(0, 255), randint(0, 255), randint(0, 255))
            center, radius = self.random_circle()
            self.data = Circle.CircleData(radius,center,color)
        elif not(data is None):
            self.data = copy.deepcopy(data)
        else:
            raise Exception('''You should either provide both 
            random as false, and data or neither of them''')

    def draw(self):
        return draw.circle(*self.data.center, self.data.radius)

    def intersects(self, other:Figure):
        if(other.figure_type == FigureType.Circle):
            center = self.data.center
            other_center = other.data.center
            distance = sqrt(
                (center[0]-other_center[0])**2 +
                (center[1]-other_center[1])**2)
            return distance < (self.data.radius + other.data.radius)
    
    def covers(self, other):
        if(other.figure_type == FigureType.Circle):
            center = self.data.center
            other_center = other.data.center
            distance = sqrt(
                (center[0]-other_center[0])**2 +
                (center[1]-other_center[1])**2)
            R = self.data.radius
            r = other.data.radius
            return distance + r <= R

    def random_circle(self):
        center = [randint(1, Figure.max_size[i]-1) for i in range(0, 2)]
        tmp = [512-item for item in center]
        max_rad = min(center + tmp)
        if max_rad < 10:
            center, radius = self.random_circle()
        else:
            radius = randint(10, max_rad)
        return [center, radius]
