"""
The following determines the next state of a given cell in a CAM.

The ruleset takes in a collection of rules specifying neighborhoods, as well as the configurations of
said neighborhood that yield an "on" or "off" state on the cell a ruleset is being applied to.

@author: jrpotter
@date: May 31st, 2015
"""
import enum
import itertools as it

import numpy as np


class Ruleset:
    """
    The primary class of this module, which saves configurations of cells that yield the next state.

    The ruleset will take in configurations defined by the user that specify how a cell's state should change,
    depending on the given neighborhood and current state. For example, if I have a configuration that states

    [[0, 0, 0]
    ,[1, 0, 1]
    ,[1, 1, 1]
    ]

    must match exactly for the center cell to be a 1, then each cell is checked for this configuration, and its
    state is updated afterward (note the above is merely for clarity; a configuration is not defined as such). Note
    configurations are checked until a match occurs, in a FIFO manner.
    """

    class Method(enum.Enum):
        """
        Specifies how a ruleset should be applied to a given cell.

        * A match declares that a given configuration must match exactly for the cell to be considered on.
        * A tolerance specifies that a configuration must match within a given percentage to be considered on.
        * A specification allows the user to define a custom function which must return a boolean, declaring
          whether a cell should be on or off. This function is given the current cell's state, as well as
          the state of the cell's neighbors.

        """
        MATCH       = 0
        TOLERATE    = 1
        SATISFY     = 2
        ALWAYS_PASS = 3

    def __init__(self, method):
        """
        @grid: Every ruleset is bound to a grid, which a ruleset is applied to.
        @method: One of the values defined in the RulesetMethod enumeration. View class for description.
        """
        self.method = method
        self.configurations = []

    def addConfiguration(self, grid, next_state, offsets):
        """
        Creates a configuration and saves said configuration.
        """
        config = Configuration(grid, next_state, offsets)
        self.configurations.append(config)

    def applyTo(self, plane, *args):
        """
        Depending on the set method, applies ruleset to each cell in the plane.

        Note we first compute all neighborhoods in a batch manner and then test that a configuration
        passes on the supplied neighborhood.

        @args: If our method is TOLERATE, we pass in a value in set [0, 1]. This specifies the threshold between a
               passing (i.e. percentage of matches in a configuration is > arg) and failing. If our method is SATISFY,
               arg should be a function returning a BOOL, which takes in a current cell's value, and the
               value of its neighbors.
        """
        master = plane.grid.flat

        for config in self.configurations:

            # Construct neighborhoods
            #
            # After profiling with a previous version, I found that going through each index and totaling the number
            # of active states was taking much longer than I liked. Instead, we compute as many neighborhoods as possible
            # simultaneously, avoiding explicit summation via the "sum" function, at least for each state separately.
            #
            # Because the states are now represented as numbers, we instead convert each number to their binary representation
            # and add the binary representations together. We do this in chunks of 9, depending on the number of offsets, so
            # no overflowing of a single column can occur. We can then find the total of the ith neighborhood by checking the
            # sum of the ith index of the summation of every 9 chunks of numbers (this is done a row at a time).

            # TODO: Config offsets should be flat index, bit offset



            neighborhoods = []

            values = []
            for f_index, offset in config.offsets:
                val = plane.f_bits([f_index])
                values.append(int(val[offset+1:] + val[:offset]))

            # Chunk into groups of 9 and sum all values
            chunks = [values[i:i+9] for i in range(0, len(values), 9)]
            summands = map(sum, chunks)

            # Construct neighborhoods for each value in list




            if self.method == Ruleset.Method.MATCH:
                vfunc = self._matches
            elif self.method == Ruleset.Method.TOLERATE:
                vfunc = self._tolerates
            elif self.method == Ruleset.Method.SATISFY:
                vfunc = self._satisfies
            elif self.method == Ruleset.Method.ALWAYS_PASS:
                vfunc = lambda *args: True

            # Apply the function if possible
            passed, state = config.passes(f_index, grid, vfunc, *args)
            if passed:
                return state

        # If no configuration passes, we leave the state unchanged
        return grid.flat[f_index]

    def _matches(self, f_index, f_grid, indices, states):
        """
        Determines that neighborhood matches expectation exactly.

        Note this functions like the tolerate method with a tolerance of 1.
        """
        return not np.count_nonzero(f_grid[indices] ^ states)

    def _tolerates(self, f_index, f_grid, indices, states, tolerance):
        """
        Determines that neighborhood matches expectation within tolerance.

        We see that the percentage of actual matches are greater than or equal to the given tolerance level. If so, we
        consider this cell to be alive. Note tolerance must be a value 0 <= t <= 1.
        """
        non_matches = np.count_nonzero(f_grid[indices] ^ states)
        return (non_matches / len(f_grid)) >= tolerance

    def _satisfies(self, f_index, f_grid, indices, states, valid_func):
        """
        Allows custom function to relay next state of given cell.

        The passed function is supplied the list of 2-tuple elements, of which the first is a Cell and the second is
        the expected state as declared in the Neighborhood, as well as the grid and cell in question.
        """
        return valid_func(f_index, f_grid, indices, states)

