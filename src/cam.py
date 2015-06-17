"""
Top level module representing a Cellular Automata Machine.

The CAM consists of a number of cell planes that allow for increasingly complex cellular automata.
This is the top-level module that should be used by anyone wanting to work with fifth, and provides
all methods needed (i.e. supported) to interact/configure with the cellular automata directly.

Displays can happen via matplotlib's animation library or the ncurses lib. Note both will support
tracing/echoing/multi-dimensional displays

@date: June 01, 2015
"""
import enum

import plane
import display

class CAM:
    """
    Represents a Cellular Automata Machine (CAM).

    A CAM consists of a series of "cell planes" which represent a separate numpy grid instance. There
    should always be at least one cell plane, dubbed the "master", since all other planes cannot be handled
    directly, but instead mirror the master plane, and reflect these changes after a given number of
    "ticks."

    A tick represents an interval of time after which all states of a given set of cell planes should be
    updated. should be updated, Certain planes may or may not change every tick, but instead on every
    nth tick, allowing for more sophisticated views such as ECHOing and TRACing.
    """
    class Show(enum.Enum):
        """
        Display method.
        """
        NONE    = 0
        CONSOLE = 1
        WINDOW  = 2

    def __init__(self, cps=1, states=100, dimen=2):
        """
        @cps:    Cell planes. By default this is 1, but can be any positive number. Any non-positive number
                 is assumed to be 1.
        @states: The number of cells that should be included in any dimension. The number of total states
                 will be cps * states^dimen
        @dimen:  The dimensions of the cellular automata. For example, for an N-tuple array, the dimension is N.
        """
        pl_cnt = max(cps, 1)
        grid_dimen = (states,) * dimen

        self.planes = [plane.Plane(grid_dimen) for _ in range(pl_cnt)]
        self.master = self.planes[0]
        self.ticks = [(0, 1)]
        self.total = 0

    def tick(self, rules, *args):
        """
        Modify all states in a given CAM "simultaneously".

        The tick function should be called whenever we want to change the current status of the grid.
        Every time the tick is called, the ruleset is applied to each cell and the next set of states
        is placed into the master grid. Depending on the timing specifications set by the user, this
        may also change secondary cell planes (the master, by default, is always updated on each tick).
        """
        self.total += 1
        for i, j in self.ticks:
            if self.total % j == 0:
                self.planes[i].dirty = True
                rules.apply_to(self.planes[i], *args)

    def randomize(self):
        """
        Convenience function to randomize individual planes.
        """
        self.master.randomize()
        for p in self.planes[1:]:
            p.grid = self.master.grid

    def start(self, show, **kwargs):
        """
        Delegate how to initiate running the CAM.
        """
        if show == CAM.Show.NONE:
            while True:
                self.tick(**kwargs)
        elif show == CAM.Show.CONSOLE:
            display.ConsoleDisplay(self, **kwargs).run()
        elif show == CAM.Show.WINDOW:
            display.WindowDisplay(self, **kwargs).run()

