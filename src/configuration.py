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
from collections import namedtuple

class Configuration:
    """
    Represents an expected neighborhood; to be compared to an actual neighborhood in a CAM.

    A configuration allows exact specification of a neighborhood, not the actual state of a neighborhood.
    It is merely used for reference by a ruleset, which takes in a series of configurations and
    the next state of a cell depending on a configuration.
    """

    # An offset contains the flat_offset, which refers to the bitarray of the plane.grid.flat that
    # a given offset is pointing to. The bit_offset refers to the index of the bitarray at the
    # given flat_offset. State describes the expected state at the given (flat_offset, bit_offset).
    Offset = namedtuple('Offset', ['flat_offset', 'bit_offset', 'state'])

    def __init__(self, next_state, **kwargs):
        """
        @next_state: Represents the next state of a cell given a configuration passes.
                     This should be an [0|1|Function that returns 0 or 1]
        @kwargs    : If supplied, should be a dictionary containing an 'offsets' key, corresponding
                     to a dictionary of offsets (they should be coordinates in N-dimensional space
                     referring to the offsets checked in a given neighborhood) with an expected
                     state value and a 'shape' key, corresponding to the shape of the grid in question.
        """
        self.offsets = []
        self.next_state = next_state
        if 'shape' in kwargs and 'offsets' in kwargs:
            self.extend_offsets(kwargs['shape'], kwargs['offsets'])

    def extend_offsets(shape, offsets):
        """
        Allow for customizing of configuration.

        For easier indexing, we convert the coordinates into a 2-tuple coordinate, where the first
        index corresponds to the the index of the flat grid, and the second refers to the bit offset
        of the value at the first coordinate.
        """
        for coor, bit in offsets.items():
            flat_index, gridprod = 0, 1
            for i in reversed(range(len(coor[:-1]))):
                flat_index += coor[i] * gridprod
                gridprod *= shape[i]
            self.offsets.append(Offset(flat_index, coor[-1], bit))

    def passes(self, f_index, grid, vfunc, *args):
        """
        Checks if a given configuration passes, and if so, returns the next state.

        @vfunc is an arbitrary function that takes in a flattened grid, a list of indices, and a list of values (which,
        if zipped with indices, correspond to the expected value of the cell at the given index). The function should
        merely verify that a list of indices "passes" some expectation.

        For example, if an "exact match" function is passed, it should merely verify that the cells at the passed indices
        exactly match the exact expectated cells in the list of values. It will return True or False depending.
        """
        # We ensure all indices are within the given grid
        indices = (f_index + self.offsets) % grid.size

        # Note the distinction between success and next_state here; vfunc (validity function) tells whether the given
        # configuration passes. If it does, no other configurations need to be checked and the next state is returned.
        success = vfunc(f_index, grid.flat, indices, self.states, *args)
        if callable(self.next_state):
            return (success, self.next_state(f_index, grid.flat, indices, self.states, *args))
        else:
            return (success, self.next_state)


