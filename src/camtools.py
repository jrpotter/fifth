"""

@author: jrpotter
@date: June 01, 2015
"""
import numpy as np

def flatten(coordinates, grid):
    """
    Given the coordinates of a matrix, returns the index of the flat matrix.
    """
    index = 0
    for i in range(len(coordinates)):
        index += coordinates[i] * np.prod(grid.shape[i+1:], dtype=np.int32)

    return index


def unflatten(index, grid):
    """
    Given an index of a flat matrix, returns the corresponding coordinates.
    """
    coordinates = []
    for i in range(len(grid.shape)):
        tmp = np.prod(grid.shape[i+1:], dtype=np.int32)
        coordinates.append(index // tmp)
        index -= tmp * coordinates[-1]

    return tuple(coordinates)


def comp_add(coor1, coor2):
    """
    Adds components of coordinates element-wise.
    """
    return tuple(map(sum, zip(coor1, coor2)))
