"""


"""
from bitplane import Bitplane


class CAM:
    """
    Represents a Cellular Automata Machine (CAM).

    The CAM consists of any number of bit planes that allow for increasingly complex cellular automata.
    This is the top-level module that should be used by anyone wanting to work with fifth, and provides
    all methods needed (i.e. supported) to interact/configure the cellular automata as desired.
    """

    def __init__(self, bps=1, dimen=(100,100)):
        """

        """
        self._dimen = dimen
        self._bitplanes = [BitPlane(dimen) for i in bps]
        self._master = self._bitplanes[0].grid if bps > 0 else None


    def tick(self, ruleset, neighborhood):
        """
        The tick function should be called whenever we want to change the current status of the grid.

        Every time the tick is called, the ruleset is applied to each cell and the next configuration
        is placed into the master grid. Depending on the timing specifications set by the user, this
        may also change secondary bitplanes (the master is always updated on each tick).
        """
        pass


