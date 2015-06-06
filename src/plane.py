"""
Wrapper of a numpy array of bits.

For the sake of efficiency, rather than work with an (m x m x ... x m) N-dimensional grid, we instead work with
a 1D array of size (N-1)^m and reshape the grid if ever necessary. All bits of any given row is represented by
a number whose binary representation expands to the given number. A 1 at index i in turn corresponds to an on
state at the ith index of the given row. This holds for 0 as well.

For example, given a 100 x 100 CAM, we represent this underneath as a 1-D array of 100 integers, each of which's
binary expansion will be 100 bits long (and padded with 0's if necessary).

@author: jrpotter
@date: June 05, 2015
"""
import numpy as np
import bitmanip as bm

class Plane:
    """
    Represents a bit plane, with underlying usage of numpy arrays.

    The following allows conversion between our given representation of a grid, and the user's expected
    representation of a grid. This allows accessing of bits in the same manner as one would access a
    numpy grid, without the same bloat as a straightforward N-dimensional grid of booleans for instance.
    """

    def __init__(self, shape):
        """
        Construction of a plane. There are three cases:

        If shape is the empty tuple, we have an undefined plane. Nothing is in it.
        If shape is length 1, we have a 1D plane. This is represented by a single number.
        Otherwise, we have an N-D plane. Everything operates as expected.
        """
        self.shape = shape

        if len(shape) == 0:
            self.grid = None
        elif len(shape) == 1:
            self.grid = 0
        else:
            self.grid = np.zeros(shape[:-1], dtype=np.object)

    def __getitem__(self, idx):
        """
        Indices supported are the same as those of the numpy array, except for when accessing an individual bit.

        When reaching the "last" dimension of the given array, we access the bit of the number at the second
        to last dimension, since we are working in (N-1)-dimensional space. Unless this last dimension is reached,
        we always return a plane object (otherwise an actual 0 or 1).
        """

        # Passed in coordinates, access incrementally
        # Note this could be a tuple of slices or numbers
        if type(idx) is tuple:
            tmp = self
            for i in idx:
                tmp = tmp[i]
            return tmp

        # Reached last dimension, return bits instead
        elif len(self.shape) == 1:
            bits = bm.bits_of(self.grid, self.shape[0])[idx]
            if isinstance(idx, slice):
                return list(map(int, bits))
            else:
                return int(bits)

        # Simply relay to numpy methods
        # We check if we encounter a list or number as opposed to a tuple, and allow further indexing if desired.
        else:
            tmp = self.grid[idx]
            try:
                plane = Plane(tmp.shape + self.shape[-1:])
                plane.grid = tmp.flat
            except AttributeError:
                plane = Plane(self.shape[-1:])
                plane.grid = tmp

            return plane

    def f_bits(self, f_index, str_type=True):
        """
        Return the binary representation of the given number at the supplied index.

        If the user wants a string type, we make sure to pad the returned number to reflect
        the actual states at the given index.
        """
        value = bin(self.planes[0].flat[f_index])[2:]
        if not str_type:
            return int(value)
        else:
            return "{}{}".format("0" * (self.shape[-1] - len(value)), value)


    def _flatten(coordinates):
        """
        Given the coordinates of a matrix, returns the index of the flat matrix.

        This is merely a convenience function to convert between N-dimensional space to 1D.
        TODO: Delete this method?
        """
        index = 0
        gridprod = 1
        for i in reversed(range(len(coordinates))):
            index += coordinates[i] * gridprod
            gridprod *= self.dimen[i]

        return index

    def randomize(self):
        """
        Sets values of grid to random values.

        Since numbers of the grid may be larger than numpy can handle natively (i.e. too big
        for C long types), we use the python random module instead.
        """
        if len(self.shape) > 0:
            import random as r
            max_u = bm.max_unsigned(self.shape[-1])
            if len(self.shape) == 1:
                self.grid = r.randrange(0, max_u)
            else:
                self.grid = np.array([r.randrange(0, max_u) for i in range(len(self.grid))])

    def bitmatrix(self):
        """

        """
        pass
