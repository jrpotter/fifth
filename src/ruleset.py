"""



@author: jrpotter
@date: May 31st, 2015
"""
import copy
import enum
import numpy as np


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

    @staticmethod
    @np.vectorize
    def update(cell, rules, neighborhood, *args):
        """
        Allow for batch processing of rules.

        We choose our processing function based on the specified rule and update every cell in the grid simultaneously
        via a vectorization.
        """
        tmp = copy.deepcopy(cell)
        if rules.method == Rule.MATCH:
            tmp.value = rules.matches(cell, neighborhood, *args)
        elif rules.method == Rule.TOLERATE:
            tmp.value = rules.tolerate(cell, neighborhood, *args)
        elif rules.method == Rule.SATISFY:
            tmp.value = rules.satisfies(cell, neighborhood, *args)

        return tmp


    def __init__(self, method):
        """

        """
        self.method = method


    def matches(self, cell, neighborhood):
        """
        Determines that neighborhood matches expectation exactly.

        Note this is just like the tolerate method with a tolerance of 1, but
        recoding allows for short circuiting.
        """
        residents = neighborhood.neighbors(cell)
        for resident in residents:
            if resident[0].value != resident[1]:
                return False

        return True


    def tolerate(self, cell, neighborhood, tolerance):
        """
        Determines that neighborhood matches expectation within tolerance.

        We see that the percentage of actual matches are greater than or equal to the given tolerance level. If so, we
        consider this cell to be alive. Note tolerance must be a value 0 <= t <= 1.
        """
        matches = 0
        residents = neighborhood.neighbors(cell)
        for resident in residents:
            if resident[0].value == resident[1]:
                matches += 1

        return (matches / len(residents)) >= tolerance


    def satisfies(self, cell, neighborhood, valid_func):
        """
        Allows custom function to relay next state of given cell.

        The passed function is supplied the list of 2-tuple elements, of which the first is a Cell and the second is
        the expected state as declared in the Neighborhood, as well as the grid and cell in question.
        """
        residents = neighborhood.neighbors(cell)

        return valid_func(cell, residents)


