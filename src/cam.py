"""


"""
import time
import copy

import ruleset as rs
import cell_plane as cp
import neighborhood as nh

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as ani


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
        self.master = self._planes[0]


    def start_plot(self, clock, ruleset, neighborhood, *args):
        """
        Initiates the main loop.

        The following function displays the actual graphical component (through use of matplotlib), and triggers the
        next tick for every "clock" milliseconds.
        """
        fig, ax = plt.subplots()

        ax.set_frame_on(False)
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)

        mshown = plt.matshow(self.master.to_binary(), fig.number)

        def animate(frame):
            self.tick(ruleset, neighborhood, *args)
            mshown.set_array(self.master.to_binary())
            fig.canvas.draw()

        ani.FuncAnimation(fig, animate, interval=clock)

        plt.axis('off')
        plt.show()


    def start_console(self, clock, ruleset, neighborhood, *args):
        """

        """
        while True:
            print(self.to_binary())
            time.sleep(clock / 1000)
            self.tick(ruleset, neighborhood, *args)


    def tick(self, ruleset, neighborhood, *args):
        """
        The tick function should be called whenever we want to change the current status of the grid.

        Every time the tick is called, the ruleset is applied to each cell and the next configuration
        is placed into the master grid. Depending on the timing specifications set by the user, this
        may also change secondary cell planes (the master is always updated on each tick).
        """
        self.master.grid[:] = rs.Ruleset.update(self.master.grid, ruleset, neighborhood, *args)


    def randomize(self):
        """
        Set the master grid to a random configuration.
        """
        @np.vectorize
        def v_random(cell):
            cell.value = np.random.random_integers(0, 1)
            return cell

        v_random(self.master.grid)

