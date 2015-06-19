"""
Wrapper of a bitarray.

For the sake of compactness, the use of numpy arrays have been completely abandoned as a representation
of the data. This also allows for a bit more consistency throughout the library, where I've often used
the flat iterator provided by numpy, and other times used the actual array.

The use of just a bitarray also means it is significantly more compact, indexing of a plane should be
more efficient, and the entire association between an N-1 dimensional grid with the current shape of
the plane is no longer a concern.

@date: June 05, 2015
"""
import random
import operator
import numpy as np

from functools import reduce
from bitarray import bitarray
from collections import deque


class Plane:
    """
    Represents a cell plane, with underlying usage of bitarrays.

    The following maintains the shape of a contiguous block of memory, allowing the user to interact
    with it as if it was a multidimensional array.
    """

    def __init__(self, shape, bits = None):
        """
        Construction of a plane. There are three cases:

        First, the user may pass in there own custom bitarray to allow manipulating the
        data in the same manner as it is done internally. When this happens, the product
        of the shape parameter's components must be equivalent to the length of the
        bitarray.

        Otherwise, we determine a grid based off solely the shape parameter. If shape
        is the empty tuple, we have an undefined plane. Consequently nothing is in it.

        Lastly, the most common usage will be to define an N-D plane, where N is equivalent
        to the number of components in the shape. For example, @shape = (100,100,100) means
        we have a 3-D grid with 1000000 cells in total (not necessarily in the CAM, just
        the plane in question).
        """
        # Keep track of dimensionality
        self.shape = shape
        self.N = len(shape)

        # Preprocess all index offsets instead of performing them each time accessing occurs
        prod = 1
        self.offsets = deque()
        for d in reversed(shape):
            self.offsets.appendleft(prod)
            prod *= d

        # Allow the user to override grid construction
        if bits is not None:
            if len(bits) != reduce(operator.mul, shape, 1):
                raise ValueError("Shape with incorrect dimensionality")
            self.bits = bits
        # Generate bitarray automatically
        else:
            self.bits = reduce(operator.mul, shape, 1) * bitarray('0')

        # Check if a plane has been updated recently
        # This should be changed to True if it is ever "ticked."
        self.dirty = False

    def __getitem__(self, index):
        """
        Indexing of a plane mirrors that of a numpy array.

        Unless accessing the "last" dimension of the given array, we return another plane with
        the sliced bitarray as the underlying bits parameter. This allows for chaining access operators.
        That being said, it is preferable to use a tuple for accessing as opposed to a sequence of
        bracket indexing, as this does not create as many planes in the process.

        If the "last" dimension is reached, we simply return the bit at the given index.
        """
        # Given coordinates of a grid. This may or may not access the last dimension.
        # If it does not, can simply return the new plane given the subset accessed.
        # If it does, we return the actual bit.
        if type(index) is tuple:
            offset = sum([x*y for (x,y) in zip(index, self.offsets)]) % len(self.bits)
            if len(index) == self.N:
                return self.bits[offset]
            else:
                remain = self.shape[len(index):]
                shift = self.offsets[len(index)-1]
                return Plane(remain, bits[offset:offset+shift])

        # A list accessor allows one to access multiple elements at the offsets specified
        # by the list elements. For example, for a plane P, P[[1, 4, 6]] returns a list
        # containing the 1, 4, and 6th element.
        elif type(index) is list:
            elements = []
            for idx in index:
                elements.append(self[idx])
            return elements

        # Otherwise we were passed a simply number and we access the element like normal
        # (making sure to consider the shape of the plane of course)
        elif self.N == 1:
            return self.bits[index]
        else:
            delta = self.offsets[0]
            offset = (index * delta) % len(self.bits)
            return Plane(self.shape[1:], self.bits[offset:offset+delta])

    def __setitem__(self, index, value):
        """
        Assigns a bit or slice of bits to a given index.

        Very similar to __getitem__ with a couple of caveats. Value should always
        be a single bit (either 0 or 1), but the index can still be a tuple, list,
        etc. The given value is assigned to all components of a given index.

        For example, with a plane P with shape (100, 100), P[0] = 1 sets the first
        100 elements (the 100 bits in the first row) to 1.
        """
        if type(index) is tuple:
            offset = sum([x*y for (x,y) in zip(index, self.offsets)]) % len(self.bits)
            if len(index) == self.N:
                self.bits[offset] = value
            else:
                shift = self.offsets[len(index)-1]
                self.bits[offset:offset+shift] = value

        elif type(index) is list:
            elements = []
            for idx in index:
                self[idx] = value

        elif self.N == 1:
            self.bits[index] = value
        else:
            delta = self.offsets[0]
            offset = (index * delta) % len(self.bits)
            self.bits[offset:offset+delta] = value

    def randomize(self):
        """
        Sets values of grid to random values.

        By default, newly initialized bitarrays are random, but in a weird way I'm not sure I
        understand. For example, constructing bitarrays in a loop appear to set every bitarray
        after the first to 0, and, if I put a print statement afterwards, all bitarrays maintain
        the same value. I'm not really too interested in figuring this out, so I use the alternate
        method below.
        """
        if self.N > 0:
            max_unsigned = reduce(operator.mul, self.shape, 1)
            sequence = bin(random.randrange(0, max_unsigned))[2:]
            self.bits = bitarray(sequence.zfill(max_unsigned))

    def flatten(self, coordinates):
        """
        Given coordinates, converts them to flattened value for direct bit access.

        Note this can be used for relative coordinates as well, and negative values
        are also supported fine.
        """
        if len(coordinates) != self.N:
            raise ValueError("Invalid Coordinates {}".format(coordinates))

        index = 0
        for i, coor in enumerate(coordinates):
            index += coor * self.offsets[i]

        return index % len(self.bits)

    def matrix(self):
        """
        Convert bitarray into a corresponding numpy matrix.

        This should not be used for computation! This is merely a convenience method
        for displaying out to matplotlib via the AxesImages plotting methods.
        """
        tmp = np.array(self.bits)
        return np.reshape(tmp, self.shape)

