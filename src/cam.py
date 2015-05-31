"""


"""
from cell_plane import CellPlane


class CAM:
    """
    Represents a Cellular Automata Machine (CAM).

    The CAM consists of any number of cell planes that allow for increasingly complex cellular automata.
    This is the top-level module that should be used by anyone wanting to work with fifth, and provides
    all methods needed (i.e. supported) to interact/configure the cellular automata as desired.
    """

    def __init__(self, cps=1, dimen=(100,100)):
        """

        """
        self._dimen = dimen
        self._planes = [CellPlane(dimen) for i in cps]
        self._master = self._planes[0].grid if cps > 0 else None


    def tick(self, ruleset, neighborhood, *args):
        """
        The tick function should be called whenever we want to change the current status of the grid.

        Every time the tick is called, the ruleset is applied to each cell and the next configuration
        is placed into the master grid. Depending on the timing specifications set by the user, this
        may also change secondary cell planes (the master is always updated on each tick).
        """
        self._master = ruleset.update(self._master, self.master, neighborhood, *args)

