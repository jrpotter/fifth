"""
Allow for displaying 2D/3D CAMs.

Two means of viewing the CAM are provided: either through the console via the curses
library or through a GUI display via the matplotlib library. Note the console display
only supports 2D CAMs while the GUI supports 2D/3D automata.

Both methods allow for the ability to display multiple cell planes at a time, with
additional support for ECHOs and TRACing.

@date: June 16th, 2015
"""
import time
import curses
import curses.panel

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as ani


class _Display:
    """
    The base class for visualization of the CAM.
    """

    def __init__(self, cam, clock, rules, *args):
        """
        Test for valid CAM and setup.
        """
        self.cam = cam
        if not self._valid():
            raise ValueError("Invalid Dimension for Display")

        self.clock = clock
        self.rules = rules
        self.tick_args = *args

    def _valid(self):
        """
        Ensures passed cam is supported for display type.
        """
        return True

    def run(self):
        """
        Initiate the main display loop.
        """
        pass


class ConsoleDisplay(_Display):
    """
    Displays CAM onto console via the curses library.

    Note a couple concepts go hand in hand with displaying all the bits:

    First, it is unlikely the entirety of a CAM can be displayed on the screen
    at a time, so instead the use of a pad is supported, allowing navigation
    via the arrow keys.

    Second, to provide support for color mapping and multiple planes, we use panels
    which allow for exactly this overlaying we are trying to simulate.
    """

    def __init__(self, cam, clock, rules, *args):
        """
        Here we initialize the curses library, and begin construction of the necessary panels.
        """
        super().__init__(cam, clock, rules, *args)

        # Basic Curses Setup
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)

        # Specifies the offsets the grid are taken at
        self.x = 0
        self.y = 0

        # Note we actually don't use the stdscr, but keeping
        # reference for future use
        width, height = self.cam.master.shape
        self.pad = curses.newpad(width+1, height+1)
        self.pad.nodelay(1)
        self.pad.keypad(1)

        # Construct the necessary planes
        self.panels = []
        for plane in self.cam.planes:
            self.panels.append(curses.panel.new_panel(self.pad))

    def _valid(self):
        """
        Ensures only 2D CAMs are accepted.
        """
        return len(self.cam.master.shape) == 2

    def _shift(self, ch):
        """
        Move all panels over by specified amount.

        Note we want functionality to wrap around, so we make
        sure to mod based on which direction we've gone. Directionality
        is determined by the passed character value.
        """
        if ch == curses.KEY_UP:
            self.y = (self.y + 1) % height
        elif ch == curses.KEY_DOWN:
            self.y = (self.y - 1) % height
        elif ch == curses.KEY_LEFT:
            self.x = (self.x + 1) % width
        elif ch == curses.KEY_RIGHT:
            self.x = (self.x - 1) % width

    def run(self):
        """
        Commence actual loop.

        The following draws out all panels, and, in the case of an exception
        (which could be user thrown by Ctrl-C), restores the terminal back
        to a usable state.
        """
        while True:
            try:
                # Note the user can change the size of the terminal,
                # so we query for these values every time
                max_y, max_x = stdscr.getmaxyx()

                # Navigate the plane
                # Note in the __init__ method, this was set to not block
                self._shift(pad.getch())

                # Cycle around grid
                grid = self.cam.master.grid
                grid = np.append(grid[y:], grid[:y])

                # Draw out to console
                line = 0
                for bits in grid.flat:
                    pad.move(line, 0)
                    pad.addstr((bits[x:] + bits[:x]).to01())
                    line += 1

                # Draw out to screen
                curses.panels.update_panels()
                pad.refresh(0, 0, 0, 0, max_y-1, max_x-1)

                # Prepare for next loop
                time.sleep(self.clock / 1000)
                self.tick(self.rules, *self.tick_args)

            except:
                curses.nocbreak()
                stdscr.keypad(False)
                curses.echo()
                curses.endwin()


class WindowDisplay(_Display):
    """
    Displays CAM onto window via the matplotlib library.

    We use the AxesImage object in matplotlib and constantly animate
    the graph to display the automata. Unlike the curses library, this
    class also provides support for 3D display, though note this is
    much more intensive.
    """
    def __init__(self, cam, clock, rules, *args):
        """
        Initialize matplotlib objects.
        """
        super().__init__(cam, clock, rules, *args)

        # Keep local reference for convenience
        self.fig, self.ax = plt.subplots()

        # Note we draw out planes in the reverse direction
        # for proper superimposition
        self.matrices = []
        for plane in self.cam.planes:
            mshown = plt.matshow(plane.bits(), fig.number, cmap='Greys')
            self.matrices.append(mshown)

    def _valid(self):
        """
        Ensures only 2D/3D CAMs are accepted.
        """
        return 2 <= len(self.cam.master.shape) <= 3

    def _animate(self, frame):
        """
        Display the next state of the automaton.

        Note that the framerate must be considered; one shouldn't just try to run
        the animation as fast as possible, as this callback will only be bottled up.
        The limiting factor is the tick method, which should be fast enough for reasonably
        sized CAMs (100x100 runs in <50 ms on my computer), but runs in quadratic time.
        """
        self.cam.tick(self.rules, *self.tick_args)
        if len(self.cam.master.shape) == 2:
            self.mshown.set_array(self.cam.master.bits())
            return [self.mshown]
        else:
            pass

    def run(self):
        """
        Commence actual loop.

        The following expands out each plane (from a bitarray to a matrix of bits)
        which are then displayed out via the animate function. We simply superimpose
        the necessary plots for the desired overlaying.
        """
        if len(self.cam.master.shape) == 2:
            self.ax.set_frame_on(False)
            self.ax.get_xaxis().set_visible(False)
            self.ax.get_yaxis().set_visible(False)
        else:
            pass

        ani.FuncAnimation(self.fig, self.animate, interval=self.clock)
        plt.axis('off')
        plt.show()

