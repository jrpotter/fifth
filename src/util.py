"""
A collection of utilities that can ease construction of CAMs.

@author: jrpotter
@date: June 4th, 2015
"""
import re

import ruleset as rs
import exceptions as ce


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


class CAMParser:
    """
    The following builds rulesets based on the passed string.

    Following notation is supported:
    * MCell Notation (x/y)
    * RLE Format (By/Sx)

    For reference: http://en.wikipedia.org/wiki/Life-like_cellular_automaton
    """

    RLE_FORMAT = r'B\d*/S\d*$'
    MCELL_FORMAT = r'\d*/\d*$'

    def __init__(self, notation, cam):
        """
        Parses the passed notation and saves values into members.

        @sfunc: Represents the function that returns the next given state.
        @ruleset: A created ruleset that matches always
        @offsets: Represents the Moore neighborhood corresponding to the given CAM
        """
        self.sfunc = None
        self.offsets = rs.Configuration.moore(cam.master)
        self.ruleset = rs.Ruleset(rs.Ruleset.Method.ALWAYS_PASS)

        if re.match(CAMParser.MCELL_FORMAT, notation):
            x, y = notation.split('/')
            if all(map(self._numasc, [x, y])):
                self.sfunc = self._mcell(x, y)
            else:
                raise ce.InvalidFormat("Non-ascending values in MCELL format")

        elif re.match(CAMParser.RLE_FORMAT, notation):
            B, S = map(lambda x: x[1:], notation.split('/'))
            if all(map(self._numasc, [B, S])):
                self.sfunc = self._mcell(S, B)
            else:
                raise ce.InvalidFormat("Non-ascending values in RLE format")

        else:
            raise ce.InvalidFormat("No supported format passed to parser.")

        # Add configuration to given CAM
        self.ruleset.addConfiguration(cam.master, self.sfunc, self.offsets)

    def _numasc(self, value):
        """
        Check the given value is a string of ascending numbers.
        """
        if all(map(str.isnumeric, value)):
            return ''.join(sorted(value)) == value
        else:
            return False

    def _mcell(self, x, y):
        """
        MCell Notation

        A rule is written as a string x/y where each of x and y is a sequence of distinct digits from 0 to 8, in
        numerical order. The presence of a digit d in the x string means that a live cell with d live neighbors
        survives into the next generation of the pattern, and the presence of d in the y string means that a dead
        cell with d live neighbors becomes alive in the next generation. For instance, in this notation,
        Conway's Game of Life is denoted 23/3
        """
        x, y = list(map(int, x)), list(map(int, y))
        def next_state(f_index, f_grid, indices, states, *args):
            total = sum(f_grid[indices])
            if f_grid[f_index]:
                return int(total in x)
            else:
                return int(total in y)

        return next_state

