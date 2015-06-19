import os, sys
sys.path.insert(0, os.path.join('..', 'src'))

import plane
import numpy as np


class TestProperties:
    """

    """
    def setUp(self):
        self.plane2d = plane.Plane((100, 100))
        self.plane3d = plane.Plane((100, 100, 100))

    def test_bitsLength(self):
        """
        Bit expansion.
        """
        assert len(self.plane2d.bits) == 100 * 100
        assert len(self.plane3d.bits) == 100 * 100 * 100

    def test_offsets(self):
        """
        Offsets.
        """
        assert list(self.plane2d.offsets) == [100, 1]
        assert list(self.plane3d.offsets) == [10000, 100, 1]

    def test_randomize(self):
        """
        Randomization.
        """
        bits2d = self.plane2d.bits
        bits3d = self.plane3d.bits
        self.plane2d.randomize()
        self.plane3d.randomize()

        assert bits2d != self.plane2d.bits
        assert bits3d != self.plane3d.bits
        assert len(self.plane2d.bits) == 100 * 100
        assert len(self.plane3d.bits) == 100 * 100 * 100


class TestIndexing:
    """

    """
    def setUp(self):
        self.plane2d = plane.Plane((100, 100))
        self.plane3d = plane.Plane((100, 100, 100))

    def test_tupleAssignment(self):
        """
        Tuple Assignment.
        """
        self.plane2d[(1, 0)] = 1
        self.plane3d[(1, 0, 0)] = 1

    def test_listAssignment(self):
        """
        List Assignment.
        """
        self.plane2d[[0]] = 1
        self.plane3d[[0]] = 1
        self.plane2d[[[(4, 5)], 5, (2, 2)]] = 1
        self.plane3d[[[(4, 5)], 5, (2, 2)]] = 1

    def test_singleAssignment(self):
        """
        Single Assignment.
        """
        self.plane2d[0][0] = 1
        self.plane3d[0][0] = 1

    def test_tupleAccessing(self):
        """
        Tuple Accessing.
        """
        self.plane2d[(1, 0)] = 1
        assert self.plane2d[(1, 0)] == 1

        self.plane3d[(1, 0)] = 1
        for i in range(10):
            assert self.plane3d[(1, 0, i)] == 1

    def test_listAccessing(self):
        """
        List Accessing.
        """
        self.plane2d[[(0, 4), (1, 5)]] = 1
        assert self.plane2d[[(0, 4), (1, 5), (1, 6)]] == [1, 1, 0]

        self.plane3d[[(0, 4)]] = 1
        assert self.plane3d[[(0, 4, 1), (0, 4, 9), (1, 6, 0)]] == [1, 1, 0]

    def test_singleAccessing(self):
        """
        Single Accessing.
        """
        self.plane2d[0] = 1
        for i in range(10):
            assert self.plane2d[0][i] == 1

    def test_flatten(self):
        """
        Flatten indices.
        """
        assert self.plane2d.flatten((0, 0)) == 0
        assert self.plane2d.flatten((-1, 0)) == 9900
        assert self.plane2d.flatten((1, 1)) == 101
        assert self.plane3d.flatten((0, 0, 0)) == 0
        assert self.plane3d.flatten((-1, 0, 0)) == 990000
        assert self.plane3d.flatten((1, 1, 1)) == 10101

