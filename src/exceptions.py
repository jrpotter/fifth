"""


@author: jrpotter
@date: June 4th, 2015
"""

class InvalidFormat(Exception):
    """
    Called when parsing an invalid format.

    For example, in MCell and RLE, numbers should be in ascending order.
    """

    def __init__(self, value):
        """

        """
        self.value = value

    def __str__(self):
        """

        """
        return repr(self.value)
