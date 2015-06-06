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

from bitarray import bitarray


class Plane:
    """
    Represents a bit plane, with underlying usage of numpy arrays.

    The following allows conversion between our given representation of a grid, and the user's expected
    representation of a grid. This allows accessing of bits in the same manner as one would access a
    numpy grid, without the same bloat as a straightforward N-dimensional grid of booleans for instance.
    """

    def __init__(self, shape, grid = None):
        """
        Construction of a plane. There are three cases:

        If shape is the empty tuple, we have an undefined plane. Nothing is in it.
        If shape is length 1, we have a 1D plane. This is represented by a single number.
        Otherwise, we have an N-D plane. Everything operates as expected.
        """
        self.grid = grid
        self.shape = shape
        self.N = 0 if not len(shape) else shape[-1]

        if self.grid is None:
            if len(shape) == 1:
                self.grid = self.N * bitarray('0')
            else:
                self.grid = np.empty(shape[:-1], dtype=np.object)
                for i in range(self.grid.size):
                    self.grid.flat[i] = bitarray(self.N)

    def __getitem__(self, index):
        """
        Indices supported are the same as those of the numpy array, except for when accessing an individual bit.

        When reaching the "last" dimension of the given array, we access the bit of the number at the second
        to last dimension, since we are working in (N-1)-dimensional space. Unless this last dimension is reached,
        we always return a plane object (otherwise an actual 0 or 1).

        Note this function is much slower than accessing the grid directly. To forsake some convenience for the
        considerable speed boost is understandable; access by plane only for this convenience.
        """

        # Given coordinates of a grid. This may or may not access the last dimension.
        # If it does not, can simply return the new plane given the subset accessed.
        # If it does, we access up to the bitarray, then access the desired bit(s)
        if type(index) is tuple:
            if len(index) == len(self.shape):
                b_array = self.grid[index[:-1]]
                return b_array[index[-1]]
            else:
                subgrid = self.grid[index]
                return Plane(subgrid.shape + (self.N,), subgrid)

        # If we've reached the last dimension, the grid of the plane is just a bitarray
        # (we remove an additional dimension and instead store the bitarray for space's sake).
        # If a list of elements are passed, we must access them individually (bitarray does
        # not have built in support for this).
        elif len(self.shape) == 1:
            if type(index) is list:
                return list(map(lambda x: self.grid[x], index))
            else:
                return self.grid[index]

        # Any other means of indexing simply indexes the grid as expected, and wraps
        # the result in a plane object for consistent accessing. An attribute error
        # can occur once we reach the last dimension, and try to determine the shape
        # of a bitarray
        tmp = self.grid[index]
        try:
            return Plane(tmp.shape + (self.N,), tmp)
        except AttributeError:
            return Plane((self.N,), tmp)

    def randomize(self):
        """
        Sets values of grid to random values.

        Since numbers of the grid may be larger than numpy can handle natively (i.e. too big
        for C long types), we use the python random module instead.
        """
        if len(self.shape) > 0:
            import random as r
            max_u = 2**self.N - 1
            if len(self.shape) == 1:
                self.grid = r.randrange(0, max_u)
            else:
                tmp = np.array([r.randrange(0, max_u) for i in range(len(self.grid))])
                self.grid = tmp.reshape(self.grid.shape)

