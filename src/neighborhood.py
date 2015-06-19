"""
A neighborhood is a collection of cells around a given cell.

The neighborhood is closely related to a configuration, which
defines how a neighborhood is expected to look. One can think
of a neighborhood as an instantiation of a given configuration,
as it contains a focus cell and the cells that should be considered
when determing the focus cell's next state.

@date: June 18, 2015
"""

class Neighborhood:
    """
    The neighborhood is a wrapper class that stores information regarding a particular cell.
    Offsets must be added separate from instantiation, since it isn't always necessary to
    perform this computation in the first place (for example, if an ALWAYS_PASS flag is passed
    as opposed to a MATCH flag).
    """
    def __init__(self, index):
        """
        Initializes the center cell.

        Offsetted cells belonging in the given neighborhood must be added separately.
        """
        self.total = 0
        self.index = index
        self.neighbors = []

    def populate(self, offsets, plane):
        """
        Given the plane and offsets, determines the cells in the given neighborhood.

        Note this is a relatively expensive operation, especially if called on every cell
        in a CAM every tick. Instead, consider using the provided class methods which
        shift through the bitarray instead of recomputing offsets
        """
        self.neighbors = plane[offsets]
        self.total = len(self.neighbors)

    @classmethod
    def get_neighborhoods(cls, plane, offsets):
        """
        Given the list of offsets, return a list of neighborhoods corresponding to every cell.

        Since offsets should generally stay fixed for each cell in a plane, we first flatten
        the coordinates (@offsets should be a list of tuples) relative to the first component
        and cycle through all cells.

        NOTE: If all you need are the total number of cells in each neighborhood, call the
        get_totals method instead, which is significantly faster.
        """
        neighborhoods = []

        if plane.N > 0:
            f_offsets = list(map(plane.flatten, offsets))
            for i in range(len(plane.bits)):
                neighborhood = Neighborhood(i)
                for j in range(len(f_offsets)):
                    neighborhood.neighbors.append(plane.bits[j])
                    plane.bits[j] += 1
                neighborhood.total = len(neighborhood.neighbors)
                neighborhoods.append(neighborhood)

        return neighborhoods

    @classmethod
    def get_totals(cls, plane, offsets):
        """
        Returns the total number of neighbors for each cell in a plane.

        After profiling with a previous version, I found that going through each index and totaling the number
        of active states was taking much longer than I liked. Instead, we compute as many neighborhoods as possible
        simultaneously, avoiding explicit summation via the "sum" function, at least for each state separately.

        Because the states are now represented as binary values, we instead add the binary representations together.
        And since offsets are generally consistent between each invocation of the "tick" function, we can add a row
        at a time. For example, given a plane P of shape (3, 3) and the following setup:

        [[0, 1, 1, 0, 1]
        ,[1, 0, 0, 1, 1]    ALIGN    11010    SUM
        ,[0, 1, 1, 0, 0]  =========> 11000 =========> 32111
        ,[1, 0, 0, 1, 0]             10101
        ,[0, 0, 0, 0, 1]
        ]

        with focus cell (1, 1) in the middle and offsets (-1, 0), (1, 0), (-1, 1), we can align the cells according to the above.
        The resulting sum states there are 3 neighbors at (1, 1), 2 neighbors at (1, 2), and 1 neighbor at (1, 3), (1, 4), and (1, 0).

        We do this in chunks of 9, depending on the number of offsets, so no overflowing of a single column can occur.
        We can then find the total of the ith neighborhood by checking the sum of the ith index of the summation of every
        9 chunks of numbers (this is done at the Nth-1 dimension).
        """
        neighborhoods = []

        # In the first dimension, we have to simply loop through and count for each bit
        if 0 < plane.N <= 1:
            for i in range(len(plane.bits)):
                neighborhoods.append(sum([plane.bits[i+j] for j in offsets]))
        else:
            for level in range(plane.shape[0]):

                # Since working in N dimensional space, we calculate the totals at a
                # rate of N-1. We do this by generalizing the above doc description, and
                # limit our focus to the offsetted subplane adjacent to the current level,
                # then slicing the returned set of bits accordingly
                neighboring = []
                for offset in offsets:
                    adj_level = level + offset[0]
                    sub_plane = plane[adj_level]
                    sub_index = sub_plane.flatten(offset[1:])
                    sequence = sub_plane.bits[sub_index:] + sub_plane.bits[:sub_index]
                    neighboring.append(int(sequence.to01()))

                # Collect our totals, breaking up each set of neighborhood totals into 9
                # and then adding the resulting collection back up (note once chunks have
                # been added, we add each digit separately (the total reduced by factor of 9))
                totals = [0] * (plane.offsets[0])
                chunks = map(sum, [neighboring[i:i+9] for i in range(0, len(neighboring), 9)])
                for chunk in chunks:
                    padded_chunk = map(int, str(chunk).zfill(len(totals)))
                    totals = map(sum, zip(totals, padded_chunk))

                # Neighboring totals now align with original grid
                neighborhoods += list(totals)

        return neighborhoods
