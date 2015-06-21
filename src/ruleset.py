import enum
import numpy as np
import configuration as c

from bitarray import bitarray


class Ruleset:
    """
    A bundle of configurations.

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

    def apply_to(self, plane, *args):
        """
        Depending on the set method, applies ruleset to each cell in the plane.

        @args: If our method is TOLERATE, we pass in a value in set [0, 1]. This specifies the threshold between a
               passing (i.e. percentage of matches in a configuration is > arg) and failing. If our method is SATISFY,
               arg should be a function returning a BOOL, which takes in a current cell's value, and the
               value of its neighbors.
        """

        # These are the states of configurations that pass (note if all configurations
        # fail for any state, the state remains the same)
        next_plane = plane.bits.copy()

        # These are the states we attempt to apply a configuration to
        # Since totals are computed for a configuration at once, we save
        # which states do not pass for each configuration
        current_states = enumerate(plane.bits)
        for config in self.configurations:

            totals = c.Neighborhood.get_totals(plane, config.offsets)

            # Determine which function should be used to test success
            if self.method == Ruleset.Method.MATCH:
                vfunc = config.matches
            elif self.method == Ruleset.Method.TOLERATE:
                vfunc = config.tolerates
            elif self.method == Ruleset.Method.SATISFY:
                vfunc = config.satisfies
            elif self.method == Ruleset.Method.ALWAYS_PASS:
                vfunc = lambda *args: True

            next_states = []
            for index, state in current_states:

                # Passes a mostly uninitialized neighborhood to the given function
                # Note if you need actual states of the neighborhood, make sure to
                # call the neighborhood's populate function
                neighborhood = c.Neighborhood(index)
                neighborhood.total = totals[index]

                # Apply changes to for any successful configurations
                success, to_state = config.passes(plane, neighborhood, vfunc, *args)
                if success:
                    next_plane[index] = to_state
                else:
                    next_states.append((index, state))

            current_states = next_states

        # All configurations tested, transition plane
        plane.bits = next_plane

