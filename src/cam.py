"""
Top level module representing a Cellular Automata Machine.

The CAM consists of any number of cell planes that allow for increasingly complex cellular automata.
This is the top-level module that should be used by anyone wanting to work with fifth, and provides
all methods needed (i.e. supported) to interact/configure the cellular automata as desired.

@author: jrpotter
@date: June 01, 2015
"""
import time
import copy

import ruleset as rs

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as ani


class CAM:
    """
    Represents a Cellular Automata Machine (CAM).

    A CAM consists of a series of "cell planes" which represent a separate numpy grid instance. There
    should always be at least one cell plane, dubbed the "master", since all other planes cannot be handled
    directly, but instead mirror the master plane, and reflect these changes after a given number of
    "ticks."

    A tick represents an interval of time after which all states should be updated, and, therefore, all
    cell planes should be updated. Certain planes may or may not change every tick, but instead on every
    nth tick, allowing for more sophisticated views such as ECHOing and TRACE-ing.
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

        self.planes = np.zeros((plane_count,) + grid_dimen, dtype='int32')
        self.master = self.planes[0]


    def randomize(self, propagate=True):
        """
        Set the master grid to a random configuration.

        If propagate is set to True, also immediately change all other cell planes to match.
        """
        self.master[:] = np.random.random_integers(0, 1, self.master.shape)
        for plane in self.planes[1:]:
            plane[:] = self.master


    def tick(self, rules, *args):
        """
        Modify all states in a given CAM "simultaneously".

        The tick function should be called whenever we want to change the current status of the grid.
        Every time the tick is called, the ruleset is applied to each cell and the next set of states
        is placed into the master grid. Depending on the timing specifications set by the user, this
        may also change secondary cell planes (the master is always updated on each tick).
        """
        tmp = np.copy(self.master)
        for i in range(len(self.master.flat)):
            tmp.flat[i] = rules.applyTo(i, self.master, *args)

        self.master[:] = tmp


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

        mshown = plt.matshow(self.master, fig.number, cmap='Greys')

        def animate(frame):
            self.tick(rules, *args)
            mshown.set_array(self.master)
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
            print(self.master)
            time.sleep(clock / 1000)
            self.tick(rules, *args)


