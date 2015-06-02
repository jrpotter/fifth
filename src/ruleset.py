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



def flatten(coordinates, grid):
    """
    Given the coordinates of a matrix, returns the index of the flat matrix.

    This is merely a convenience function to convert between N-dimensional space to 1D.
    """
    index = 0
    gridprod = 1
    for i in reversed(range(len(coordinates))):
        index += coordinates[i] * gridprod
        gridprod *= grid.shape[i]

    return index



class Configuration:
    """
    Represents an expected neighborhood; to be compared to an actual neighborhood in a CAM.

    A configuration allows exact specification of a neighborhood, not the actual state of a neighborhood.
    It is merely used for reference by a ruleset, which takes in a series of configurations and
    the next state of a cell depending on a configuration.
    """

    # Possible states a cell can take
    #
    # If a configuration passes, the cell's state will be on or off if ON or OFF was passed respectively.
    # If IGNORE, then the state remains the same, but no further configurations will be checked by the
    # ruleset.
    ON  = 1
    OFF = 0


    def __init__(self, grid, next_state, offsets={}):
        """

        @next_state: Represents the next state of a cell given a configuration passes.
                     This should be an [ON|OFF|Function that returns ON or Off]

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
            f_offsets.append(flatten(k, grid))

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


    @classmethod
    def moore(cls, grid, value=ON):
        """
        Returns a neighborhood corresponding to the Moore neighborhood.

        The Moore neighborhood consists of all adjacent cells. In 2D, these correspond to the 8 touching cells
        N, NE, E, SE, S, SW, S, and NW. In 3D, this corresponds to all cells in the "backward" and "forward"
        layer that adjoin the nine cells in the "center" layer. This concept can be extended to N dimensions.

        Note the center cell is excluded, so the total number of offsets are 3^N - 1.
        """
        offsets = {}
        variants = ([-1, 0, 1],) * len(grid.shape)
        for current in it.product(*variants):
            if any(current):
                offsets[current] = value

        return offsets


    @classmethod
    def neumann(cls, grid, value=ON):
        """
        Returns a neighborhood corresponding to the Von Neumann neighborhood.

        The Von Neumann neighborhood consists of adjacent cells that directly share a face with the current cell.
        In 2D, these correspond to the 4 touching cells N, S, E, W. In 3D, we include the "backward" and "forward"
        cell. This concept can be extended to N dimensions.

        Note the center cell is excluded, so the total number of offsets are 2N.
        """
        offsets = {}
        variant = [0] * len(grid.shape)
        for i in range(len(variant)):
            for j in [-1, 1]:
                variant[i] = j
                offsets[tuple(variant)] = value
            variant[i] = 0

        return offsets



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
        MATCH    = 0
        TOLERATE = 1
        SATISFY  = 2


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


    def applyTo(self, f_index, grid, *args):
        """
        Depending on a given method, applies ruleset to a cell.

        @cell_index: The index of the cell in question, as offset by self.grid.flat. That means the index should be
                     a single number (not a tuple!).

        @args:       If our method is TOLERATE, we pass in a value in set [0, 1]. This specifies the threshold between a
                     passing (i.e. percentage of matches in a configuration is > arg) and failing. If our method is SATISFY,
                     arg should be a function returning a BOOL, which takes in a current cell's value, and the
                     value of its neighbors.

        """
        for config in self.configurations:

            # Determine the correct function to use
            vfunc = None
            if self.method == Ruleset.Method.MATCH:
                vfunc = self._matches
            elif self.method == Ruleset.Method.TOLERATE:
                vfunc = self._tolerates
            elif self.method == Ruleset.Method.SATISFY:
                vfunc = self._satisfies

            # Apply the function if possible
            if vfunc is not None:
                passed, state = config.passes(f_index, grid, vfunc, *args)
                if passed:
                    return state
            else:
                break

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
        non_matches = np.count_nonzero(f_grid[inices] ^ states)
        return (non_matches / len(f_grid)) >= tolerance


    def _satisfies(self, f_index, f_grid, indices, states, valid_func):
        """
        Allows custom function to relay next state of given cell.

        The passed function is supplied the list of 2-tuple elements, of which the first is a Cell and the second is
        the expected state as declared in the Neighborhood, as well as the grid and cell in question.
        """
        return valid_func(f_index, f_grid, indices, states)


