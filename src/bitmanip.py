"""

@author: jrpotter
@date: June 5th, 2015
"""
def max_unsigned(bit_count):
    """

    """
    return 2**bit_count - 1


def bits_of(value, size = 0):
    """

    """
    base = bin(value)[2:]
    if size > len(base):
        return "{}{}".format("0" * (size - len(base)), base)
    else:
        return base

def cycle(itr, offset):
    """

    """
    return itr[:offset] + itr[offset+1:]
