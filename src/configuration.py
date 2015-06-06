"""
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
with the ALWAYS_PASS flag set in the given ruleset the configuration is bundled in.

@date: June 5th, 2015
"""
import numpy as np
from itertools import product
from collections import namedtuple


class Neighborhood:
    """
    Specifies the cells that should be considered when referencing a particular cell.

    The neighborhood is a wrapper class that stores information regarding a particular cell.
    Offsets must be added separate from instantiation, since it isn't always necessary to
    perform this computation in the first place (for example, if an ALWAYS_PASS flag is passed
    as opposed to a MATCH flag).

    It may be helpful to consider a configuration as a template of a neighborhood, and a neighborhood
    as an instantiation of a configuration (one with concrete values as opposed to templated ones).
    """

    def __init__(self, flat_index, bit_index, total):
        """
        Initializes the center cell.

        Offsetted cells belonging in the given neighborhood must be added separately.
        """
        self.states = None
        self.bit_indices = None
        self.flat_indices = None

        self.total = total
        self.bit_index = bit_index
        self.flat_index = flat_index


    def process_offsets(self, plane, offsets):
        """
        Given the plane and offsets, determines the cells in the given neighborhood.

        This is rather expensive to call on every cell in a grid, so should be used with caution.
        Namely, this is useful when we need to determine matches within a threshold, since total cells
        of a neighborhood are precomputed in the ruleset.

        For example, if we need an exact match of a configuration, we have to first process all the
        offsets of a neighborhood to determine that it indeed matches the configuration (if this was
        not called, self.offsets would remain empty).
        """
        flat_indices, bit_indices, _ = zip(*offsets)

        states = []
        for i in range(len(flat_indices)):
            bit_index = bit_indices[i]
            flat_index = flat_indices[i]
            states.append(plane.grid.flat[flat_index][bit_index])

        self.states = np.array(states)
        self.bit_indices = np.array(bit_indices)
        self.flat_indices = np.array(flat_indices)


class Configuration:
    """
    Represents an expected neighborhood; to be compared to an actual neighborhood in a CAM.

    A configuration allows specification of a neighborhood, not the actual state of a neighborhood.
    It is merely used for reference by a ruleset, which takes in a series of configurations and
    returns the state referenced by the first configuration that passes.
    """

    # An offset contains the flat_offset, which refers to the bitarray of the plane.grid.flat that
    # a given offset is pointing to. The bit_offset refers to the index of the bitarray at the
    # given flat_offset. State describes the expected state at the given (flat_offset, bit_offset).

    Offset = namedtuple('Offset', ['flat_offset', 'bit_offset', 'state'])


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
        offsets = []
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
            flat_index, bit_index = plane.flatten(coor)
            self.offsets.append(Configuration.Offset(flat_index, bit_index, bit))


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
        neighborhood.process_offsets(plane, self.offsets)
        bits = np.array([offset[2] for offset in self.offsets])

        return not np.count_nonzero(bits ^ neighborhood.states)


    def tolerates(self, plane, neighborhood, tolerance):
        """
        Determines that neighborhood matches expectation within tolerance.

        We see that the percentage of actual matches are greater than or equal to the given tolerance level. If so, we
        consider this cell to be alive. Note tolerance must be a value 0 <= t <= 1.
        """
        neighborhood.process_offsets(plane, self.offsets)
        bits = np.array([offset[2] for offset in self.offsets])
        non_matches = np.count_nonzero(bits ^ neighborhood.states)

        return (non_matches / len(bits)) >= tolerance


    def satisfies(self, plane, neighborhood, valid_func, *args):
        """
        Allows custom function to relay next state of given cell.

        The passed function is passed the given plane and a neighborhood corresponding to the cell
        being processed at the moment.
        """
        return valid_func(plane, neighborhood, *args)

