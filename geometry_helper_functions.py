"""Helper functions for geometric operations, e.g. return distance b/w points, etc."""
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


def triangle_area(p1: [int, int], p2: [int, int], p3: [int, int]) -> float:
    """Returns area of triangle given by 3 points"""
    char_mat = np.array([
        [p1[0], p1[1], 1],
        [p2[0], p2[1], 1],
        [p3[0], p3[1], 1]
    ])
    return abs(0.5 * np.linalg.det(char_mat))
