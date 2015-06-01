"""


@author: jrpotter
@date: May 31st, 2015
"""
import itertools


class Neighborhood:
    """
    The following represents the cells that must be considered when applying a ruleset, as well as the
    values expected in a ruleset.

    Since neighborhoods can be made arbitrarily complex, we allow extending in all directions. For example,
    the basic Moore neighborhood comprises of the 8 cells surrounding the center, but what if we wanted
    these 8 and include the cell north of north? The following enables this:

    m_neighborhood = Neighborhood.moore(2)
    m_neighborhood.extend({(-2, 0): True})

    This allows indexing at levels beyond 3D, which the Cells enumeration does not allow, though visualization
    at this point isn't possible.
    """

    class NeighborhoodKey:
        """
        Allows proper sorting of neighborhoods.

        Lists should be returned in order, where cell's with smaller indices (in most significant axis first)
        are listed before cell's with larger ones. For example, in a 3D grid, the neighbors corresponding to:

            offsets = (-1, -1, -1), (-1, 1, 0), (-1, 0, -1), and (1, 0, -1)

        are returned in the following order:

            offsets = (-1, -1, -1), (-1, 0, -1), (1, 0, -1), (-1, 1, 0)

        since the z-axis is most significant, followed by the y-axis, and lastly the x-axis.
        """
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
             return self.compare(self.obj, other.obj) < 0
        def __gt__(self, other):
            return self.compare(self.obj, other.obj) > 0
        def __eq__(self, other):
            return self.compare(self.obj, other.obj) == 0
        def __le__(self, other):
            return self.compare(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return self.compare(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return self.compare(self.obj, other.obj) != 0
        def compare(self, other):
            for i in reversed(range(len(a))):
                if a[i] < b[i]:
                    return -1
                elif a[i] > b[i]:
                    return 1
            return 0


    def __init__(self, grid, wrap_around=True):
        """
        Sets up an empty neighborhood.

        Initially, no cells are included in a neighborhood. All neighborhoods must be extended.
        Note the offsets have a tuple as a key representing the position being offsetted by, and as a value,
        the current state the given cell at the offset is checked to be.
        """
        self.grid = grid
        self.offsets = {}
        self.wrap_around = wrap_around


    def neighbors(self, cell):
        """
        Returns all cells in the given neighborhood.

        The returned cells are grouped with the value the cell is checked to be (a 2-tuple (Cell, value) pair).
        These are sorted based on the NeighborhoodKey comparison class defined above.
        """
        cells = []
        for k in sorted(self.offsets.keys()):
            position = [sum(x) for x in zip(cell.index, k)]
            for i in range(len(position)):
                if self.wrap_around:
                    position[i] = position[i] % self.grid.shape[i]
                elif i < 0 or i >= self.grid.shape[i]:
                    break
            else:
                cells.append((self.grid[tuple(position)], self.offsets[k]))

        return cells


    def extend(self, offsets, strict=False):
        """
        Adds new offsets to the instance member offsets.

        We complain if the strict flag is set to True and an offset has already been declared with a different value.
        """
        if not strict:
            self.offsets.update(offsets)
        else:
            for k in offsets.keys():
                value = self.offsets.get(k, None)
                if value is None:
                    self.offsets[k] = offsets[k]
                elif value != offsets[k]:
                    raise KeyError


    @classmethod
    def moore(cls, grid, wrap_around=True, value=True):
        """
        Returns a neighborhood corresponding to the Moore neighborhood.

        The Moore neighborhood consists of all adjacent cells. In 2D, these correspond to the 8 touching cells
        N, NE, E, SE, S, SW, S, and NW. In 3D, this corresponds to all cells in the "backward" and "forward"
        layer that adjoin the nine cells in the "center" layer. This concept can be extended to N dimensions.

        Note the center cell is excluded, so the total number of offsets are 3^N - 1.
        """
        offsets = {}
        variants = ([-1, 0, 1],) * len(grid.shape)
        for current in itertools.product(*variants):
            if any(current):
                offsets[current] = value

        m_neighborhood = cls(grid, wrap_around)
        m_neighborhood.extend(offsets)

        return m_neighborhood


    @classmethod
    def neumann(cls, grid, wrap_around=True, value=True):
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

        n_neighborhood = cls(grid, wrap_around)
        n_neighborhood.extend(offsets)

        return n_neighborhood

