import sys
import time
import curses
import itertools
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as ani


class _Display:
    """
    Allow for displaying 2D/3D CAMs.

    Two means of viewing the CAM are provided: either through the console via the curses
    library or through a GUI display via the matplotlib library. Note the console display
    only supports 2D CAMs while the GUI supports 2D/3D automata.

    Both methods allow for the ability to display multiple cell planes at a time, with
    additional support for ECHOs and TRACing.
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
        self.tick_args = args

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
    at a time, so instead we emulate the use of a pad, allowing navigation
    via the arrow keys.

    Second, to provide support for color mapping and multiple planes, we use panels
    which allow for exactly this overlaying we are trying to simulate.
    """

    def __init__(self, cam, clock, rules, *args):
        """
        Here we initialize the curses library, and begin construction of the necessary overlays.
        """
        super().__init__(cam, clock, rules, *args)

        # Basic Curses Setup
        self.stdscr = curses.initscr()
        self.stdscr.keypad(True)
        self.stdscr.nodelay(True)

        # Other setup
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        curses.use_default_colors()

        # Specifies the offsets the grid are taken at
        self.x, self.y = 0, 0
        self.width, self.height = self.cam.master.shape

        # Construct the necessary planes
        self.overlays = []
        for i, plane in enumerate(self.cam.planes):
            pad = curses.newpad(self.width+1, self.height+1)
            self.overlays.append(pad)
            if i > 0:
                self.overlays[i-1].overlay(pad)

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
            self.y = (self.y + 1) % self.height
        elif ch == curses.KEY_DOWN:
            self.y = (self.y - 1) % self.height
        elif ch == curses.KEY_LEFT:
            self.x = (self.x + 1) % self.width
        elif ch == curses.KEY_RIGHT:
            self.x = (self.x - 1) % self.width

    def _draw_overlay(self, overlay, plane):
        """
        Draw the grid onto the overlay.

        Wherever a one occurs, we make sure to draw it. Otherwise, we create a transparent
        spot so any overlays below can be seen.
        """
        overlay.clear()

        line = 0
        for i in range(plane.shape[0]):
            overlay.move(line, 0)
            line += 1

            # Make sure to account for movement
            y_offset = ((i + self.y) % plane.shape[0]) * plane.shape[1]
            bits = plane.bits[y_offset:y_offset+plane.shape[1]]
            cycle = bits[self.x:] + bits[:self.x]

            # Draw only active states
            for k, g in itertools.groupby(cycle):
                values = list(g)
                if any(values):
                    overlay.addstr('+' * len(values))
                else:
                    pass
                    y, x = overlay.getyx()
                    overlay.move(y, x + len(values))

    def run(self):
        """
        Commence actual loop.

        The following draws out all panels, and, in the case of an exception
        (which could be user thrown by Ctrl-C), restores the terminal back
        to a usable state.
        """
        try:
            while True:

                # Note the user can change the size of the terminal,
                # so we query for these values every time
                max_y, max_x = self.stdscr.getmaxyx()

                # Navigate the plane
                # Note in the __init__ method, this was set to not block
                self._shift(self.stdscr.getch())

                # Cycle around grid
                for i, plane in enumerate(self.cam.planes):
                    if plane.dirty:
                        plane.dirty = False
                        self._draw_overlay(self.overlays[i], plane)
                        self.overlays[i].noutrefresh(0, 0, 0, 0, max_y-1, max_x-1)

                # Prepare for next loop
                curses.doupdate()
                time.sleep(self.clock / 1000)
                self.cam.tick(self.rules, *self.tick_args)

        except:
            self.stdscr.keypad(False)
            curses.nocbreak()
            curses.echo()
            curses.endwin()
            print("Exception: ", sys.exc_info()[0])
            raise


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
            mshown = plt.matshow(plane.matrix(), self.fig.number, cmap='Greys')
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
            self.matrices[0].set_array(self.cam.master.matrix())
            return [self.matrices[0]]
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

        ani.FuncAnimation(self.fig, self._animate, interval=self.clock)
        plt.axis('off')
        plt.show()

