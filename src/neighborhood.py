"""


"""
import enum


class Cells(enum.Enum):
    """
    Allows for specification of which cells should be considered in a 2D or 3D matrix.

    For example, to specify the CENTER and NORTH cells, we consider CENTER | NORTH. It
    does not make sense to use FORWARD and BACKWARD in a 2D matrix, as that specifies
    looking up and down a bitplane for further cells.

    For higher level dimensions, forgo use of this enumeration entirely, as described in
    the Neighborhood class.
    """

    # 2D & 3D
    CENTER      = 1 << 0
    NORTH       = 1 << 1
    NORTHEAST   = 1 << 2
    EAST        = 1 << 3
    SOUTHEAST   = 1 << 4
    SOUTH       = 1 << 5
    SOUTHWEST   = 1 << 6
    WEST        = 1 << 7
    NORTHWEST   = 1 << 8
    NORTH       = 1 << 9

    # 3D
    FORWARD     = 1 << 10
    BACKWARD    = 1 << 11


class Neighborhood:
    """
    The following represents the cells that must be considered when applying a ruleset.

    Since neighborhoods can be made arbitrarily complex, we allow extending in all directions. For example,
    the basic Moore neighborhood comprises of the 8 cells surrounding the center, but what if we wanted
    these 8 and include the cell north of north? The following enables this:

    ...


    This allows indexing at levels beyond 3D, which the Cells enumeration does not allow, though visualization
    at this point isn't possible.
    """
    def __init__(self, grid):

        pass

