"""


@author: jrpotter
@date: May 31st, 2015
"""
import camtools as ct
import itertools as it


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

    def __init__(self, wrap_around=True):
        """
        Sets up an empty neighborhood.

        Initially, no cells are included in a neighborhood. All neighborhoods must be extended.
        Note the offsets have a tuple as a key representing the position being offsetted by, and as a value,
        the current state the given cell at the offset is checked to be.
        """
        self.offsets = {}
        self.wrap_around = wrap_around


    def neighbors(self, index, grid):
        """
        Returns all cells in the given neighborhood.

        The returned list of indices represent the index in question, the value at the given index, and
        the expected value as defined in the offsets.
        """
        indices = []
        for key in sorted(self.offsets.keys()):
            if self.wrap_around:
                f_index = (key + index) % len(grid.flat)
                indices.append((f_index, grid.flat[f_index], self.offsets[key]))
            else:
                pass

        return indices


    def extend(self, offsets, grid, strict=False):
        """
        Adds new offsets to the instance member offsets.

        We complain if the strict flag is set to True and an offset has already been declared with a different value.
        Note also that all offsets are indices of the flattened matrix. This allows for quick row indexing as opposed
        to individual coordinates.
        """
        f_offsets = {ct.flatten(k, grid): v for k, v in offsets.items()}
        if not strict:
            self.offsets.update(f_offsets)
        else:
            for k in f_offsets.keys():
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
        for current in it.product(*variants):
            if any(current):
                offsets[current] = value

        m_neighborhood = cls(wrap_around)
        m_neighborhood.extend(offsets, grid)

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

        n_neighborhood = cls(wrap_around)
        n_neighborhood.extend(offsets, grid)

        return n_neighborhood

