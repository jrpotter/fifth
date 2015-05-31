"""




"""
import numpy as np
import matplotlib.pyplot as plt


class Cell:
    """
    Represents a "cell" in a CellPlane.

    Note we keep track of the index for vectorization purposes. By maintaining each index
    and batch updating via the given index, we can much more efficiently update the entire
    cell plane.
    """
    def __init__(self, value, *index):
        self.value = value
        self.index = index


class CellPlane:
    """
    A CellPlane represents a layer of the grids that can be placed on top of one another in a 2D CAM.

    The use of multiple cell plane allow for more intricate states of life and death, though there
    exists only a single master cell plane that controls the others. That is, the master cell plane has
    a CAM ruleset applied to it, and the other cell planes merely copy the master, though this can
    be delayed and have different color mappings.

    For example, by setting a delay of two ticks on the second cell plane of a 2-level CAM configuration,
    one can allow for ECHOing, providing a more intuitive sense of "velocity" based on the master.

    That is not to say one could not have multiple CAM's operating simultaneously though. We can consider
    a configuration to consist of an arbitrary number of planes, of which one is the master, but multiple
    masters can exist in separate CAMs that can interact with one another.
    """

    @staticmethod
    @np.vectorize
    def _populate(*indices):
        """
        The following joins indices in N-dimensions together.

        This information is stored in a cell (with initial value False) in order for batch processing
        to be performed when actually updating values and computing whether a cell is on or off. For
        example, if exploring a 4D array, we want to be able to know which cells we need to check the
        status of, but this is relative to the current cell, whose position we do not know unless that
        information is stored with the current cell.
        """
        return Cell(False, *indices)


    def __init__(self, dimen):
        """

        """
        self.grid = CellPlane._populate(*np.indices(dimen))

