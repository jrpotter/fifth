import re
import ruleset as r
import configuration as c


class CAMParser:
    """
    Parses CAM languages for quick construction of CAMs.

    For example, when considering CAMs of life, most follow the same formula; check
    the total number of cells in a given neighborhood and if there are a certain
    number around an off cell, turn it on, and vice versa. Thus the parser takes
    in a generic language regarding this and constructs the necessary functions for
    the user.

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
        self.offsets = c.Configuration.moore(cam.master)
        self.ruleset = r.Ruleset(r.Ruleset.Method.ALWAYS_PASS)

        if re.match(CAMParser.MCELL_FORMAT, notation):
            x, y = notation.split('/')
            if all(map(self._numasc, [x, y])):
                self.sfunc = self._mcell(x, y)
            else:
                raise ValueError("Non-ascending values in MCELL format")

        elif re.match(CAMParser.RLE_FORMAT, notation):
            B, S = map(lambda x: x[1:], notation.split('/'))
            if all(map(self._numasc, [B, S])):
                self.sfunc = self._mcell(S, B)
            else:
                raise ValueError("Non-ascending values in RLE format")

        else:
            raise ValueError("No supported format passed to parser.")

        # Add configuration to given CAM
        config = c.Configuration(self.sfunc, plane=cam.master, offsets=self.offsets)
        self.ruleset.configurations.append(config)

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
        def next_state(plane, neighborhood, *args):
            if plane.bits[neighborhood.flat_index]:
                return int(neighborhood.total in x)
            else:
                return int(neighborhood.total in y)

        return next_state

