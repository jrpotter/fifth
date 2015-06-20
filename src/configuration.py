import numpy as np

from bitarray import bitarray
from itertools import product
from collections import namedtuple


class Neighborhood:
    """
    A neighborhood is a collection of cells around a given cell.

    The neighborhood is closely related to a configuration, which
    defines how a neighborhood is expected to look. One can think
    of a neighborhood as an instantiation of a given configuration,
    as it contains a focus cell and the cells that should be considered
    when determing the focus cell's next state.


    Offsets must be added separate from instantiation, since it isn't always necessary to
    perform this computation in the first place (for example, if an ALWAYS_PASS flag is passed
    as opposed to a MATCH flag).
    """
    def __init__(self, index):
        """
        Initializes the center cell.

        Offsetted cells belonging in the given neighborhood must be added separately.
        """
        self.total = 0
        self.index = index
        self.neighbors = bitarray()

    def populate(self, plane, offsets):
        """
        Given the plane and offsets, determines the cells in the given neighborhood.

        Note this is a relatively expensive operation, especially if called on every cell
        in a CAM every tick. Instead, consider using the provided class methods which
        shift through the bitarray instead of recomputing offsets
        """
        self.neighbors = bitarray()
        for offset in offsets:
            f_index = plane.flatten(offset) + self.index
            self.neighbors.append(plane.bits[f_index % len(plane.bits)])

        self.total = len(self.neighbors)

    @classmethod
    def get_neighborhoods(cls, plane, offsets):
        """
        Given the list of offsets, return a list of neighborhoods corresponding to every cell.

        Since offsets should generally stay fixed for each cell in a plane, we first flatten
        the coordinates (@offsets should be a list of tuples) relative to the first component
        and cycle through all cells.

        NOTE: If all you need are the total number of cells in each neighborhood, call the
        get_totals method instead, which is significantly faster.
        """
        neighborhoods = []

        if plane.N > 0:
            f_offsets = list(map(plane.flatten, offsets))
            for i in range(len(plane.bits)):
                neighborhood = Neighborhood(plane.unflatten(i))
                for j in range(len(f_offsets)):
                    neighborhood.neighbors.append(plane.bits[j])
                    plane.bits[j] += 1
                neighborhood.total = len(neighborhood.neighbors)
                neighborhoods.append(neighborhood)

        return neighborhoods

    @classmethod
    def get_totals(cls, plane, offsets):
        """
        Returns the total number of neighbors for each cell in a plane.

        After profiling with a previous version, I found that going through each index and totaling the number
        of active states was taking much longer than I liked. Instead, we compute as many neighborhoods as possible
        simultaneously, avoiding explicit summation via the "sum" function, at least for each state separately.

        Because the states are now represented as binary values, we instead add the binary representations together.
        And since offsets are generally consistent between each invocation of the "tick" function, we can add a row
        at a time. For example, given a plane P of shape (3, 3) and the following setup:

        [[0, 1, 1, 0, 1]
        ,[1, 0, 0, 1, 1]    ALIGN    11010    SUM
        ,[0, 1, 1, 0, 0]  =========> 11000 =========> 32111
        ,[1, 0, 0, 1, 0]             10101
        ,[0, 0, 0, 0, 1]
        ]

        with focus cell (1, 1) in the middle and offsets (-1, 0), (1, 0), (-1, 1), we can align the cells according to the above.
        The resulting sum states there are 3 neighbors at (1, 1), 2 neighbors at (1, 2), and 1 neighbor at (1, 3), (1, 4), and (1, 0).

        We do this in chunks of 9, depending on the number of offsets, so no overflowing of a single column can occur.
        We can then find the total of the ith neighborhood by checking the sum of the ith index of the summation of every
        9 chunks of numbers (this is done at the Nth-1 dimension).
        """
        n_counts = []

        # In the first dimension, we have to simply loop through and count for each bit
        if 0 < plane.N <= 1:
            for i in range(len(plane.bits)):
                n_counts.append(sum([plane.bits[i+j] for j in offsets]))
        else:
            for level in range(plane.shape[0]):

                # Since working in N dimensional space, we calculate the totals at a
                # rate of N-1. We do this by generalizing the above doc description, and
                # limit our focus to the offsetted subplane adjacent to the current level,
                # then slicing the returned set of bits accordingly
                neighboring = []
                for offset in offsets:
                    adj_level = level + offset[0]
                    sub_plane = plane[adj_level]
                    sub_index = sub_plane.flatten(offset[1:])
                    sequence = sub_plane.bits[sub_index:] + sub_plane.bits[:sub_index]
                    neighboring.append(int(sequence.to01()))

                # Collect our totals, breaking up each set of neighborhood totals into 9
                # and then adding the resulting collection back up (note once chunks have
                # been added, we add each digit separately (the total reduced by factor of 9))
                totals = [0] * (plane.offsets[0])
                chunks = map(sum, [neighboring[i:i+9] for i in range(0, len(neighboring), 9)])
                for chunk in chunks:
                    padded_chunk = map(int, str(chunk).zfill(len(totals)))
                    totals = map(sum, zip(totals, padded_chunk))

                # Neighboring totals now align with original grid
                n_counts += list(totals)

        return n_counts


class Configuration:
    """
    Represents an expected neighborhood; to be compared to an actual neighborhood in a CAM.

    A configuration defines an expectation of a cell's neighborhood, and the cell's new state if is passes
    this expectation.

    Multiple configurations are tested one after another in a ruleset, on every cell individually,
    to determine what the next state of a given cell should be. If no configuration passes, the
    cell remains the same. Otherwise it is either turned on or off. To see the usefulness of this,
    consider the following:

    [[0, 1, 1]
    ,[1, 1, 0] --> 1
    ,[0, 1, 1]
    ]

    Here we're saying a cell's neighborhood must match exactly the above for the cell to remain a
    one. But how do we allow two possibilities to yield a 1? We add an additional configuration!

    Often times, a single configuration is perfectly fine, and the exact bits are irrelevant. This
    is the case for all life-life automata for example. In this case, we create a configuration
    with the always_pass flag set in the given ruleset the configuration is bundled in.
    """

    @staticmethod
    def moore(plane, value=1):
        """
        Returns a neighborhood corresponding to the Moore neighborhood.

        The Moore neighborhood consists of all adjacent cells. In 2D, these correspond to the 8 touching cells
        N, NE, E, SE, S, SW, S, and NW. In 3D, this corresponds to all cells in the "backward" and "forward"
        layer that adjoin the nine cells in the "center" layer. This concept can be extended to N dimensions.
        Note the center cell is excluded, so the total number of offsets are 3^N - 1.
        """
        offsets = {}
        variants = ([-1, 0, 1],) * len(plane.shape)
        for current in product(*variants):
            if any(current):
                offsets[current] = value

        return offsets

    @staticmethod
    def neumann(plane, value=1):
        """
        Returns a neighborhood corresponding to the Von Neumann neighborhood.

        The Von Neumann neighborhood consists of adjacent cells that directly share a face with the current cell.
        In 2D, these correspond to the 4 touching cells N, S, E, W. In 3D, we include the "backward" and "forward"
        cell. This concept can be extended to N dimensions.

        Note the center cell is excluded, so the total number of offsets are 2N.
        """
        offsets = {}
        variant = [0] * len(plane.shape)
        for i in range(len(variant)):
            for j in [-1, 1]:
                variant[i] = j
                offsets[tuple(variant)] = value
            variant[i] = 0

        return offsets

    def __init__(self, next_state, **kwargs):
        """
        @next_state: Represents the next state of a cell given a configuration passes.
                     This should be an [0|1|Function that returns 0 or 1]
        @kwargs    : If supplied, should be a dictionary containing an 'offsets' key, corresponding
                     to a dictionary of offsets (they should be coordinates in N-dimensional space
                     referring to the offsets checked in a given neighborhood) with an expected
                     state value and a 'plane' key, corresponding to the plane in question.
        """
        self.offsets = []
        self.sequence = bitarray()
        self.next_state = next_state
        if 'plane' in kwargs and 'offsets' in kwargs:
            self.extend_offsets(kwargs['plane'], kwargs['offsets'])

    def extend_offsets(self, plane, offsets):
        """
        Allow for customizing of configuration.

        For easier indexing, we convert the coordinates into a 2-tuple coordinate, where the first
        index corresponds to the the index of the flat grid, and the second refers to the bit offset
        of the value at the first coordinate.
        """
        for coor, bit in offsets.items():
            self.offsets.append(coor)
            self.sequence.append(bit)

    def passes(self, plane, neighborhood, vfunc, *args):
        """
        Determines whether a passed neighborhood satisfies the given configuration.

        The configuration is considered passing or failing based on the provided vfunc; if successful,
        the bit centered in the neighborhood should be set to the next state as determined by the
        configuration.

        Note the distinction between success and next state
        vfunc denotes that the configuration passes; that is, a configuration determines the next
        state of a cell but should only be heeded if the configuration passes. The next state, which
        is either a 0, 1, or a function that returns a 0 or 1 is the actual new value of the cell.
        """
        if not vfunc(plane, neighborhood, *args):
            return (False, None)
        try:
            return (True, self.next_state(plane, neighborhood, *args))
        except TypeError:
            return (True, self.next_state)

    def matches(self, plane, neighborhood):
        """
        Determines that neighborhood matches expectation exactly.

        Note this behaves like the _tolerates method with a tolerance of 1.
        """
        neighborhood.populate(plane, self.offsets)
        return (self.sequence ^ neighborhood.neighbors).count() == 0

    def tolerates(self, plane, neighborhood, tolerance):
        """
        Determines that neighborhood matches expectation within tolerance.

        We see that the percentage of actual matches are greater than or equal to the given tolerance level. If so, we
        consider this cell to be alive. Note tolerance must be a value 0 <= t <= 1.
        """
        neighborhood.populate(plane, self.offsets)
        non_matches = self.sequence ^ neighborhood.neighbors
        return ((len(self.sequence) - non_matches.count()) / len(self.sequence)) >= tolerance

    def satisfies(self, plane, neighborhood, valid_func, *args):
        """
        Allows custom function to relay next state of given cell.

        The passed function is passed the given plane and a neighborhood corresponding to the cell
        being processed at the moment.
        """
        return valid_func(plane, neighborhood, *args)

