"""


"""
import copy
import numpy as np
import ruleset as rs
import cell_plane as cp
import neighborhood as nh


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
        cps = max(cps, 1)
        self._dimen = dimen
        self._planes = [cp.CellPlane(dimen) for i in range(cps)]
        self.master = self._planes[0].grid


    def tick(self, ruleset, neighborhood, *args):
        """
        The tick function should be called whenever we want to change the current status of the grid.

        Every time the tick is called, the ruleset is applied to each cell and the next configuration
        is placed into the master grid. Depending on the timing specifications set by the user, this
        may also change secondary cell planes (the master is always updated on each tick).
        """
        self.master[:] = rs.Ruleset.update(self.master, ruleset, neighborhood, *args)


    def randomize(self):
        """
        Set the master grid to a random configuration.
        """
        @np.vectorize
        def v_random(cell):
            cell.value = np.random.random_integers(0, 1)
            return cell

        v_random(self.master)


    def console_display(self):
        """
        A convenience method used to display the grid onto the console.

        This should not be called frequently; I haven't benchmarked it but I do not anticipate this
        running very well for larger grids.
        """
        vfunc = np.vectorize(lambda x: int(x.value))
        print(vfunc(self.master))

