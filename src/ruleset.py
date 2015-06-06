"""
The following determines the next state of a given cell in a CAM.

The ruleset takes in a collection of rules specifying neighborhoods, as well as the configurations of
said neighborhood that yield an "on" or "off" state on the cell a ruleset is being applied to.

@date: May 31st, 2015
"""
import enum

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
    configurations are checked until a match occurs, in order of the configurations list.
    """

    class Method(enum.Enum):
        """
        Specifies how a ruleset should be applied to a given cell.

        * A match declares that a given configuration must match exactly for a configuration to pass
        * A tolerance specifies that a configuration must match within a given percentage to pass
        * A specification allows the user to define a custom function which must return a boolean, declaring
          whether a configuration passes. This function is given a neighborhood with all necessary information.
        * Always passing allows the first configuration to always yield a success. It is redundant to add
          any additional configurations in this case (in fact it is inefficient since neighborhoods are computer
          in advance).
        """
        MATCH       = 0
        TOLERATE    = 1
        SATISFY     = 2
        ALWAYS_PASS = 3

    def __init__(self, method):
        """
        A ruleset does not begin with any configurations; only a means of verifying them.

        @method: One of the values defined in the Ruleset.Method enumeration. View class for description.
        """
        self.method = method
        self.configurations = []

    def applyTo(self, plane, *args):
        """
        Depending on the set method, applies ruleset to each cell in the plane.

        @args: If our method is TOLERATE, we pass in a value in set [0, 1]. This specifies the threshold between a
               passing (i.e. percentage of matches in a configuration is > arg) and failing. If our method is SATISFY,
               arg should be a function returning a BOOL, which takes in a current cell's value, and the
               value of its neighbors.
        """

        # Determine which function should be used to test success
        if self.method == Ruleset.Method.MATCH:
            vfunc = self._matches
        elif self.method == Ruleset.Method.TOLERATE:
            vfunc = self._tolerates
        elif self.method == Ruleset.Method.SATISFY:
            vfunc = self._satisfies
        elif self.method == Ruleset.Method.ALWAYS_PASS:
            vfunc = lambda *args: True

        # Find the set of neighborhoods for each given configuration
        neighborhoods = [self._construct_neighborhoods(plane, config) for c in self.configurations]
        for f_idx, value in enumerate(self.plane.flat):
            for b_offset in len(self.plane.shape[-1]):
                for c_idx, config in enumerate(self.configurations):
                    n_idx = f_idx * self.plane.shape[-1] + b_offset
                    passed, state = config.passes(neighborhoods[c_idx][n_idx], vfunc, *args)
                    if passed:
                        plane[f_idx][b_offset] = state
                        break

    def _construct_neighborhoods(self, plane, config):
        """
        Construct neighborhoods

        After profiling with a previous version, I found that going through each index and totaling the number
        of active states was taking much longer than I liked. Instead, we compute as many neighborhoods as possible
        simultaneously, avoiding explicit summation via the "sum" function, at least for each state separately.

        Because the states are now represented as numbers, we instead convert each number to their binary representation
        and add the binary representations together. We do this in chunks of 9, depending on the number of offsets, so
        no overflowing of a single column can occur. We can then find the total of the ith neighborhood by checking the
        sum of the ith index of the summation of every 9 chunks of numbers (this is done a row at a time).

        TODO: Config offsets should be flat offset, bit offset
        """
        neighborhoods = []

        for f_idx, row in enumerate(plane.grid.flat):

            # Construct the current neighborhoods of each bit beforehand
            row_neighborhoods = [Neighborhood(f_idx, i) for i in range(plane.shape[-1])]

            # Note: config's offsets contain the index of the number in the plane's flat iterator
            # and the offset of the bit referring to the actual state in the given neighborhood
            offset_totals = []
            for f_offset, b_offset in config.offsets:
                row_offset = plane.f_bits(f_idx + f_offset)
                offset_totals.append(int(row_offset[b_offset+1:] + row_offset[:b_offset]))

            # Chunk into groups of 9 and sum all values
            # These summations represent the total number of states in a given neighborhood
            chunks = map(sum, [offset_totals[i:i+9] for i in range(0, len(offset_totals), 9)])
            for chunk in chunks:
                for i in range(len(row_neighborhoods)):
                    row_neighborhoods[i].total += int(chunk[i])

            # Lastly, keep neighborhoods 1D, to easily relate to the flat plane grid
            neighborhoods += row_neighborhoods

        return neighborhoods

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

