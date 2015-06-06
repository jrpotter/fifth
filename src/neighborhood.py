"""

@author: jrpotter
@date: June 5th, 2015
"""

class Neighborhood:
    """

    """
    def __init__(self, index, offsets):
        """

        """
        self.index = -1
        self.total = -1
        self.states = np.array([])
        self.indices = np.array([])

    @classmethod
    def moore(cls, grid, value=1):
        """
        Returns a neighborhood corresponding to the Moore neighborhood.

        The Moore neighborhood consists of all adjacent cells. In 2D, these correspond to the 8 touching cells
        N, NE, E, SE, S, SW, S, and NW. In 3D, this corresponds to all cells in the "backward" and "forward"
        layer that adjoin the nine cells in the "center" layer. This concept can be extended to N dimensions.

        Note the center cell is excluded, so the total number of offsets are 3^N - 1.
        """
        offsets = {}
        variants = ([-1, 0, 1],) * len(grid.shape)
        for current in it.product(*variants):
            if any(current):
                offsets[current] = value

        return offsets

    @classmethod
    def neumann(cls, grid, value=1):
        """
        Returns a neighborhood corresponding to the Von Neumann neighborhood.

        The Von Neumann neighborhood consists of adjacent cells that directly share a face with the current cell.
        In 2D, these correspond to the 4 touching cells N, S, E, W. In 3D, we include the "backward" and "forward"
        cell. This concept can be extended to N dimensions.

        Note the center cell is excluded, so the total number of offsets are 2N.
        """
        offsets = {}
        variant = [0] * len(grid.shape)
        for i in range(len(variant)):
            for j in [-1, 1]:
                variant[i] = j
                offsets[tuple(variant)] = value
            variant[i] = 0

        return offsets
