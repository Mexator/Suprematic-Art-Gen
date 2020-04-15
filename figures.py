from random import randint
from skimage import draw
from enum import Enum
from math import sqrt, sin, cos, radians
import copy
import numpy as np

class FigureType(Enum):
    Circle = 1
    Rectangle = 2
    Triangle = 3
    Cross = 4


class Figure:
    max_size = [512,512]
    figure_type = None

    def __init__(self, is_random=True, data=None):
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
    @staticmethod
    def distance(point1:[int,int],point2:[int,int]):
        return sqrt(
                (point1[0]-point2[0])**2 +
                (point1[1]-point2[1])**2)
    @staticmethod
    def seg_circle_intersection(circle, segment:[[int,int],[int,int]]):
        # http://doswa.com/2009/07/13/circle-segment-intersectioncollision.html
        # a - segment[0]
        segment_vector = np.array([[segment[1][i]-segment[0][i] for i in range(0,2)]])
        rel_pos_vector = np.array([[circle.center[i]-segment[0][i] for i in range(0,2)]])
        seg_unit = segment_vector*1/np.linalg.norm(segment_vector)
        proj_vector_len = rel_pos_vector.dot(np.transpose(seg_unit))
        if proj_vector_len < 0:
            closest = segment[0]
        elif proj_vector_len > np.linalg.norm(segment_vector):
            closest = segment[1]
        else:        
            proj_vector = proj_vector_len * seg_unit
            closest = np.array(segment[0]) + proj_vector
        if Figure.distance(closest.reshape(2,),circle.center)<circle.radius:
            return True
        return False
        


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
            center, radius = Circle.random_circle()
            self.data = Circle.CircleData(radius,center,color)
        elif not(data is None):
            self.data = copy.deepcopy(data)
        else:
            raise Exception('''You should either provide both 
            random as false, and data or neither of them''')

    def draw(self):
        return draw.circle(*self.data.center, self.data.radius)
    
    def center(self):
        return self.data.center
    
    def translate(self,delta:(int,int)):
        raise NotImplementedError('')
    def rotate(self,degrees:int):
        raise NotImplementedError('')
    def change_color(self, color:(int,int,int)):
        raise NotImplementedError('')

    def intersects(self, other:Figure):
        if(other.figure_type == FigureType.Circle):
            center = self.data.center
            other_center = other.data.center
            dist = Figure.distance(center,other_center)
            return dist < (self.data.radius + other.data.radius)
        if(other.figure_type == FigureType.Rectangle):
            return other.intersects(self)
    
    def covers(self, other):
        if(other.figure_type == FigureType.Circle):
            center = self.data.center
            other_center = other.data.center
            dist = Figure.distance(center,other_center)
            R = self.data.radius
            r = other.data.radius
            return dist + r <= R

    @staticmethod
    def random_circle():
        center = [randint(1, Figure.max_size[i]-1) for i in range(0, 2)]
        tmp = [512-item for item in center]
        max_rad = min(center + tmp)
        if max_rad < 10:
            center, radius = Circle.random_circle()
        else:
            radius = randint(10, max_rad)
        return [center, radius]

class Rectangle(Figure):
    figure_type = FigureType.Rectangle

    # Necessary data to create rectangle: 
    # circumscribed circle and two angles
    class RectangleData(Circle.CircleData):
        angles:(float,float)
        def __init__(self, r:int,c:[int,int],col:(int,int,int), thetas:(float,float)):
            super().__init__(r,c,col)
            self.angles = thetas
        def vertices(self):
            vertices_x=[]
            vertices_y=[]
            center = self.center
            vertices_x += [center[0] + self.radius*sin(radians(i)) for i in self.angles]
            vertices_x += [center[0] + self.radius*sin(radians(i+180)) for i in self.angles]

            vertices_y += [center[1] + self.radius*cos(radians(i)) for i in self.angles]
            vertices_y += [center[1] + self.radius*cos(radians(i+180)) for i in self.angles]
            return [vertices_x,vertices_y]

    def __init__(self, is_random=True,data:RectangleData=None):
        if is_random:
            color = (randint(0, 255), randint(0, 255), randint(0, 255))
            center, radius = Circle.random_circle()
            angle1 = randint(0,360)
            angle2 = randint(0,360)
            self.data = Rectangle.RectangleData(radius,center,color,(angle1,angle2))
        elif not(data is None):
            self.data = copy.deepcopy(data)
        else:
            raise Exception('''You should either provide both 
            random as false, and data or neither of them''')

    def draw(self):
        vertices_x,vertices_y = self.data.vertices()
        return draw.polygon(vertices_y,vertices_x)

    def center(self):
        return self.data.center
    
    def translate(self,delta:(int,int)):
        raise NotImplementedError('')
    def rotate(self,degrees:int):
        raise NotImplementedError('')
    def change_color(self, color:(int,int,int)):
        raise NotImplementedError('')

    def intersects(self, other:Figure):
        if(other.figure_type == FigureType.Circle):
            vertices = self.data.vertices()
            for vertice in vertices:
                if Figure.distance(vertice,other.data.center):
                    return True
            prev = vertices[0]
            for i in range(1,len(vertices)):
                cur = vertices[i]
                if(Figure.seg_circle_intersection(other.data,[prev,cur])):
                    return True
                prev = cur
            if(Figure.seg_circle_intersection(other.data,[vertices[-1],vertices[0]])):
                return True
            else:
                return False
            