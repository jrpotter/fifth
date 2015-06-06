"""

@author: jrpotter
@date: June 5th, 2015
"""

class Configuration:
    """
    Represents an expected neighborhood; to be compared to an actual neighborhood in a CAM.

    A configuration allows exact specification of a neighborhood, not the actual state of a neighborhood.
    It is merely used for reference by a ruleset, which takes in a series of configurations and
    the next state of a cell depending on a configuration.
    """

    def __init__(self, grid, next_state, offsets={}):
        """

        @next_state: Represents the next state of a cell given a configuration passes.
                     This should be an [0|1|Function that returns 0 or 1]

        @offsets:    A dictionary of offsets containing N-tuple keys and [-1, 0, 1] values.
                     Note N must be the same dimension as the grid's dimensions, as it specifies
                     the offset from any given cell in the grid.

        """
        self.next_state = next_state

        # The grid we work with is flattened, so that we can simply access single indices (as opposed
        # to N-ary tuples). This also allows for multiple index accessing via the numpy list indexing
        # method
        states = []
        f_offsets = []
        for k, v in offsets.items():
            states.append(v)
            f_offsets.append(util.flatten(k, grid))

        self.states = np.array(states)
        self.offsets = np.array(f_offsets)

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
