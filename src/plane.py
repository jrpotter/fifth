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

    def __init__(self, size, N):
        """
        Construction of a plane. There are three cases:

        If N == 0: We have an undefined plane. Nothing is in it.
        If N == 1: We have a 1D plane. This is represented by a single number.
        Otherwise: We have an N-D plane. Everything operates as expected.

        If N happens to be negative, an exception is thrown.
        """
        if N < 0:
            raise ValueError('Negative dimension nonsensical')
        elif N == 0:
            self.shape = ()
            self.grid = np.array([], dtype=np.object)
        elif N == 1:
            self.shape = (size,)
            self.grid = np.array([0], dtype=np.object)
        else:
            self.shape = (size,) * N
            self.grid = np.zeros((size**(N-1),), dtype=np.object)

    def __getitem__(self, idx):
        """
        Indices supported are the same as those of the numpy array, except for when accessing an individual bit.

        When reaching the "last" dimension of the given array, we access the bit of the number at the second
        to last dimension, since we are working in (N-1)-dimensional space. Unless this last dimension is reached,
        we always return a plane object (otherwise an actual 0 or 1).
        """

        # Passed in coordinates, access incrementally
        # Note this could be a tuple of slices or numbers
        if type(idx) in [tuple]:
            tmp = self
            for i in idx:
                tmp = tmp[i]
            return tmp

        # Reached last dimension, return bits instead
        elif len(self.shape) == 1:
            bits = bm.bits_of(self.grid[0], self.shape[0])[idx]
            if isinstance(idx, slice):
                return list(map(int, bits))
            else:
                return int(bits)

        # Simply relay to numpy methods
        # Note this doesn't necessarily return a grid in the same notion but
        # does still allow further indexing if desired. In addition, we can
        # be confident idx is either a list or a number so the final dimension
        # cannot be accessed from here
        # TODO: Reconsider this...
        else:
            full = np.reshape(self.grid, self.shape[:-1])[idx]
            tmp = cls(1, len(self.shape) - 1)
            tmp.grid = full.flat
            return tmp

    def _flatten(coordinates):
        """
        Given the coordinates of a matrix, returns the index of the flat matrix.

        This is merely a convenience function to convert between N-dimensional space to 1D.
        """
        index = 0
        gridprod = 1
        for i in reversed(range(len(coordinates))):
            index += coordinates[i] * gridprod
            gridprod *= self.dimen[i]

        return index

    def randomize(self):
        """

        """
        self.grid = np.random.random_integers(0, bm.max_unsigned(dimen), self.grid.shape)

    def bitmatrix(self):
        """

        """
        pass
