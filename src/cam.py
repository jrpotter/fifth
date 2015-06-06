"""
Top level module representing a Cellular Automata Machine.

The CAM consists of a number of cell planes that allow for increasingly complex cellular automata.
This is the top-level module that should be used by anyone wanting to work with fifth, and provides
all methods needed (i.e. supported) to interact/configure with the cellular automata directly.

@date: June 01, 2015
"""
import time
import matplotlib.pyplot as plt
import matplotlib.animation as ani


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

    def __init__(self, cps=1, states=100, dimen=2):
        """
        @cps:    Cell planes. By default this is 1, but can be any positive number. Any non-positive number
                 is assumed to be 1.
        @states: The number of cells that should be included in any dimension. The number of total states
                 will be cps * states^dimen
        @dimen:  The dimensions of the cellular automata. For example, for an N-tuple array, the dimension is N.
        """
        plane_count = max(cps, 1)
        grid_dimen = (states,) * dimen

        self.planes = [Plane(grid_dimen) for i in range(cps)]
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
                rules.applyTo(self.planes[i], *args)

    def start_plot(self, clock, rules, *args):
        """
        Initiates main graphical loop.

        The following function displays the graphical component (through use of matplotlib), and triggers the
        next tick for every "clock" milliseconds. This should only be called if the automata is 2 or 3 dimensional.
        """
        fig, ax = plt.subplots()

        ax.set_frame_on(False)
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)

        mshown = plt.matshow(self.planes[0].bits(), fig.number, cmap='Greys')

        def animate(frame):
            self.tick(rules, *args)
            mshown.set_array(self.planes[0].bits())
            return [mshown]

        ani.FuncAnimation(fig, animate, interval=clock)
        plt.axis('off')
        plt.show()

    def start_console(self, clock, rules, *args):
        """
        Initates main console loop.

        Works similarly to start_plot but prints out to the console.
        TODO: Incorporate curses, instead of just printing repeatedly.
        """
        while True:
            print(self.planes[0].bits())
            time.sleep(clock / 1000)
            self.tick(rules, *args)

