"""



@author: jrpotter
@date: May 31st, 2015
"""
from enum import Enum

class Rule(Enum):
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

    def __init__(self, method, wrap_around=True):
        """

        """
        self.method = method
        self.wrap_around = wrap_around


    def _matches(self, cell, grid, neighborhood):
        """
        Determines that neighborhood matches expectation exactly.

        Note this is just like the tolerate method with a tolerance of 1, but
        recoding allows for short circuiting.
        """
        residents = neighborhood.neighbors(cell, grid, self.wrap_around)
        for resident in residents:
            if resident[0].value != resident[1]:
                return False

        return True


    def _tolerate(self, cell, grid, neighborhood, tolerance):
        """
        Determines that neighborhood matches expectation within tolerance.

        We see that the percentage of actual matches are greater than or equal to the given tolerance level. If so, we
        consider this cell to be alive. Note tolerance must be a value 0 <= t <= 1.
        """
        matches = 0
        residents = neighborhood.neighbors(cell, grid, self.wrap_around)
        for resident in residents:
            if resident[0].value == resident[1]:
                matches += 1

        return (matches / len(residents)) >= tolerance


    def _satisfies(self, cell, grid, neighborhood, valid_func):
        """
        Allows custom function to relay next state of given cell.

        The passed function is supplied the list of 2-tuple elements, of which the first is a Cell and the second is
        the expected state as declared in the Neighborhood, as well as the grid and cell in question.
        """
        residents = neighborhood.neighbors(cell, grid, self.wrap_around)

        return valid_func(cell, grid, residents)


    @np.vectorize
    def update(self, cell, *args):
        """
        Allow for batch processing of rules.

        We choose our processing function based on the specified rule and update every cell in the grid simultaneously
        via a vectorization.
        """
        if self.method == Rule.MATCH:
            cell.value = self._matches(cell, *args)
        elif self.method == Rule.TOLERATE:
            cell.value = self._tolerate(cell, *args)
        elif self.method == Rule.SATISFY:
            cell.value = self._satisfy(cell, *args)

        return cell

