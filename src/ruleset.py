"""



@author: jrpotter
@date: May 31st, 2015
"""
import enum
import camtools


class Rule(enum.Enum):
    MATCH    = 0
    TOLERATE = 1
    SATISFY  = 2


class Ruleset:
    """
    The following determines the next state of a given cell in a CAM.

    Given a neighborhood and a tolerance level, the ruleset determines whether a given cell should be on or off after a tick.
    For example, if the tolerance level is set to 100% (i.e. neighborhoods must exactly match desired neighborhood to be on),
    then the ruleset iterates through all neighbors and verifies a match.

    For the sake of clarity, we consider a neighborhood to actually contain the "rules" for matching, and a ruleset to be the
    application of the rules as defined in the neighborhood. We state this since the actual expected values are declared in
    a neighborhood instance's offsets member.
    """

    def __init__(self, method):
        """

        """
        self.method = method


    def matches(self, index, grid, neighborhood):
        """
        Determines that neighborhood matches expectation exactly.

        Note this is just like the tolerate method with a tolerance of 1, but
        recoding allows for short circuiting.
        """
        residents = neighborhood.neighbors(index, grid)
        for resident in residents:
            if grid[resident[0]] != resident[1]:
                return False

        return True


    def tolerate(self, index, grid, neighborhood, tolerance):
        """
        Determines that neighborhood matches expectation within tolerance.

        We see that the percentage of actual matches are greater than or equal to the given tolerance level. If so, we
        consider this cell to be alive. Note tolerance must be a value 0 <= t <= 1.
        """
        matches = 0
        residents = neighborhood.neighbors(index, grid)
        for resident in residents:
            if grid[resident[0]] == resident[1]:
                matches += 1

        return (matches / len(residents)) >= tolerance


    def satisfies(self, index, grid, neighborhood, valid_func):
        """
        Allows custom function to relay next state of given cell.

        The passed function is supplied the list of 2-tuple elements, of which the first is a Cell and the second is
        the expected state as declared in the Neighborhood, as well as the grid and cell in question.
        """
        residents = neighborhood.neighbors(index, grid)
        coordinate = camtools.unflatten(index, grid)

        return valid_func(coordinate, grid, residents)


    def call(self, index, grid, neighborhood, *args):
        """
        Allow for batch processing of rules.

        We choose our processing function based on the specified rule and update every cell in the grid simultaneously
        via a vectorization.
        """
        if self.method == Rule.MATCH:
            func = self.matches
        elif self.method == Rule.TOLERATE:
            func = self.tolerate
        elif self.method == Rule.SATISFY:
            func = self.satisfies

        return int(func(index, grid, neighborhood, *args))

