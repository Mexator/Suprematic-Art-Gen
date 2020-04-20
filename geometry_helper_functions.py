"""Helper functions for geometric operations, e.g. return distance b/w points, etc."""
from math import sin, cos
import numpy as np


def distance(point1: [int, int], point2: [int, int]):
    """Returns 2D distance between 2 points"""
    point1 = np.array(point1)
    point2 = np.array(point2)
    return np.linalg.norm(point1 - point2)


def seg_circle_intersection(circle, segment: [[int, int], [int, int]]) -> bool:
    """Returns True, iff line segment, given by start and end points intersects
    given circle"""
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
    if distance(closest.reshape(2, ), circle.center) < circle.radius:
        return True
    return False


def triangle_area(p_1: [int, int], p_2: [int, int], p_3: [int, int]) -> float:
    """Returns area of triangle given by 3 points"""
    char_mat = np.array([
        [p_1[0], p_1[1], 1],
        [p_2[0], p_2[1], 1],
        [p_3[0], p_3[1], 1]
    ])
    return abs(0.5 * np.linalg.det(char_mat))


def rotation_matrix(theta):
    """Returns rotation matrix for given angle in radians"""
    return np.array([
        [cos(theta), -sin(theta)],
        [sin(theta), cos(theta)]
    ])


def line_segments_intersection(seg1: [[int, int], [int, int]],
                               seg2: [[int, int], [int, int]]) -> bool:
    """Returns True, iff 2 line segments, given by start and end points intersect
    each other"""
    o_1 = np.asarray(seg1[0])
    d_1 = np.asarray(seg1[1])-np.asarray(seg1[0])
    o_2 = np.asarray(seg2[0])
    d_2 = np.asarray(seg2[1])-np.asarray(seg2[0])

    d2_ort = d_2.dot(rotation_matrix(np.pi/2))
    d1_ort = d_1.dot(rotation_matrix(np.pi/2))

    tmp = d_1.dot(d2_ort)
    if abs(tmp) <= 1e-10:
        return False
    s = (o_2-o_1).dot(d2_ort)
    s /= tmp
    tmp = d_2.dot(d1_ort)
    if abs(tmp) <= 1e-10:
        return False
    t = (o_1-o_2).dot(d1_ort)
    t /= tmp
    return 0 < s < 1 and 0 < t < 1
