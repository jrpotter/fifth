"""




"""
import numpy as np
import matplotlib.pyplot as plt




class BitPlane:
    """
    A BitPlane represents a layer of the grids that can be placed on top of one another in a 2D CAM.

    The use of multiple bit plane allow for more intricate states of life and death, though there
    exists only a single master bit plane that controls the others. That is, the master bit plane has
    a CAM ruleset applied to it, and the other bit planes merely copy the master, though this can
    be delayed and have different color mappings.

    For example, by setting a delay of two ticks on the second bit plane of a 2-level CAM configuration,
    one can allow for ECHOing, providing a more intuitive sense of "velocity" based on the master.

    That is not to say one could not have multiple CAM's operating simultaneously though. We can consider
    a configuration to consist of an arbitrary number of planes, of which one is the master, but multiple
    masters can exist in separate CAMs that can interact with one another.
    """

    def __init__(self, *dimensions):
        """

        """
        self.grid = np.zeros(dimensions)
